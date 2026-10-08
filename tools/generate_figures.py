"""Generate the guide's editable SVG diagrams with Python's standard library."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "_static"
COLORS = {
    "input": ("#427CC0", "#F1F6FC"),
    "galaxy": ("#BA7D25", "#FCF6EB"),
    "grid": ("#278470", "#EFF8F5"),
    "feedback": ("#8260A2", "#F6F1FA"),
    "output": ("#BD5864", "#FCF2F4"),
}


class Diagram:
    def __init__(self, width, height, title, description):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>',
            '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#203344} .heading{font-weight:700;font-size:17px} .body{font-size:14px} .label{font-size:13px}</style>',
            f'<rect width="{width}" height="{height}" fill="white"/>',
        ]
        self.nodes = {}

    def panel(self, x, y, width, height, label=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="#F5F7F9" stroke="#DCE2E7"/>')
        if label:
            self.label(x + 15, y + 25, label, anchor="start")

    def box(self, name, x, y, width, height, title, lines, kind="grid", optional=False):
        stroke, fill = COLORS[kind]
        dash = ' stroke-dasharray="6 4"' if optional else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dash}/>')
        self.parts.append(f'<text x="{x+width/2}" y="{y+25}" text-anchor="middle" class="heading">{escape(title)}</text>')
        for i, line in enumerate(lines):
            self.parts.append(f'<text x="{x+width/2}" y="{y+48+i*19}" text-anchor="middle" class="body">{escape(line)}</text>')
        self.nodes[name] = {
            "n": (x + width/2, y), "s": (x + width/2, y + height),
            "w": (x, y + height/2), "e": (x + width, y + height/2),
        }

    def label(self, x, y, text, anchor="middle", color=None):
        fill = f' style="fill:{color}"' if color else ""
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="label"{fill}>{escape(text)}</text>')

    def edge(self, source, target, source_port="s", target_port="n", via=(), color="#536676", dashed=False):
        points = [self.nodes[source][source_port], *via, self.nodes[target][target_port]]
        d = "M " + " L ".join(f"{x:g} {y:g}" for x, y in points)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.7" marker-end="url(#arrow)"{dash}/>')

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT/name).write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")


def workflow():
    d = Diagram(1160, 1390, "Meraxes execution flow", "Top-down coupled snapshot workflow with a next-snapshot loop, optional thermal and 21-cm products, and final master-file assembly.")
    d.panel(280, 327, 855, 860, "Snapshot loop: dracarys()")
    stages = [
        ("launch", 20, 72, "Launch Meraxes", ["main(): initialize MPI"], "input"),
        ("params", 120, 88, "Read parameters", ["read_parameter_file()", "Run file, simulation file and defaults"], "input"),
        ("init", 237, 82, "Initialize tables and storage", ["init_meraxes() → init_storage()", "Timeline, cooling and stellar-feedback tables"], "input"),
        ("halos", 372, 92, "Read halos and update hosts", ["read_halos(); reconnect galaxies", "Sample persistent UVB feedback"], "input"),
        ("evolve", 500, 92, "Evolve galaxies", ["evolve_galaxies()", "Gas cycling, stars, feedback, BHs and mergers"], "galaxy"),
        ("prepare", 628, 95, "Prepare source and density grids", ["construct_baryon_grids() and grid readers", "NGP deposition; distributed grid assembly"], "grid"),
        ("igm", 766, 100, "Calculate thermal and ionization fields", ["ComputeTs() when enabled", "find_HII_bubbles(); update UVB history"], "grid"),
        ("tb", 907, 82, "Calculate 21-cm brightness", ["ComputeBrightnessTemperatureBox()", "delta_T when enabled"], "grid"),
        ("save", 1055, 95, "Save outputs", ["write_snapshot() and grid-output writers", "Selected catalogues/cubes; interim summaries"], "output"),
        ("master", 1280, 85, "Assemble the master file", ["Rank 0: create_master_file()", "meraxes.hdf5 → saved-product analysis"], "output"),
    ]
    for name, y, height, title, lines, kind in stages:
        d.box(name, 345, y, 505, height, title, lines, kind)
    for a, b in zip(stages, stages[1:]):
        d.edge(a[0], b[0])
    d.box("density", 900, 634, 210, 82, "Simulation grids", ["read_grid()", "Density; thermal velocities"], "input")
    d.box("products", 900, 901, 210, 110, "Derived products", ["Compute_PS()", "ConstructLightcone()", "Enabled separately"], "grid", True)
    d.edge("density", "prepare", "w", "e", color=COLORS["input"][0])
    d.edge("tb", "products", "e", "w", color=COLORS["grid"][0])
    d.edge("products", "save", "s", "e", via=[(1005, 1102.5)], color=COLORS["grid"][0])
    d.edge("save", "halos", "w", "w", via=[(245,1102.5),(245,418)], dashed=True)
    d.label(155, 743, "Next snapshot")
    d.label(690, 1216, "After the last snapshot")
    d.save("workflow.svg")


def source_flow():
    d = Diagram(1220, 675, "From galaxies to radiation grids", "Galaxy source quantities and simulation density enter separate readers before grid calculations produce ionization, thermal and 21-cm products.")
    d.box("gal", 25, 20, 350, 105, "Galaxy source state", ["Stars, SFR and effective AGN sources", "Standard or enabled stochastic treatment", "Source quantities after galaxy evolution"], "galaxy")
    d.box("ngp", 440, 20, 320, 105, "Deposit on the spatial grid", ["construct_baryon_grids()", "Nearest-grid-point cell sums", "MPI assembly"], "grid")
    d.box("sources", 835, 20, 320, 125, "Source arrays", ["stars; weighted_sfr; sfr; Pop III", "effective_bhm; effective_bhar", "Internal X-ray heating sources", "Saved arrays listed in Outputs"], "grid")
    d.box("sim", 25, 245, 350, 100, "Simulation input", ["Density contrast", "Velocity in the thermal path", "Independent of galaxy deposition"], "input")
    d.box("fields", 440, 230, 320, 125, "Calculate IGM fields", ["Thermal evolution when enabled", "Ionization and recombinations", "Persistent photoheating history", "Density and radiation sources"], "grid")
    d.box("tb", 835, 245, 320, 100, "21-cm signal", ["Co-eval brightness temperature", "Optional power spectrum and lightcone"], "grid")
    d.box("feedback", 440, 465, 320, 100, "Feedback to galaxies", ["Local UVB history → MvirCrit", "Suppress subsequent baryonic infall"], "feedback")
    d.box("out", 835, 465, 320, 100, "Saved products", ["Rank catalogues and grid files", "Linked through the master file"], "output")
    d.edge("gal","ngp","e","w")
    d.edge("ngp","sources","e","w")
    d.edge("sources","fields","s","n",via=[(995,185),(600,185)])
    d.edge("sim","fields","e","w",color=COLORS["input"][0])
    d.edge("fields","tb","e","w")
    d.edge("fields","feedback")
    d.edge("feedback","gal","w","w",via=[(10,515),(10,72.5)],color=COLORS["feedback"][0],dashed=True)
    d.edge("tb","out")
    d.label(590, 625, "Source arrays are spatial inputs; galaxy catalogue fields remain separate saved records.")
    d.save("source-flow.svg")


def galaxy_physics():
    d = Diagram(1150, 700, "Galaxy physics and radiation feedback", "Gas supply and cooling feed star formation and black holes; stellar and UV background feedback couple the galaxy and intergalactic calculations.")
    d.box("halo", 35, 25, 315, 90, "Halo assembly", ["Growth, host changes and mergers", "Baryonic gas supply"], "input")
    d.box("gas", 35, 225, 315, 110, "Gas reservoirs", ["Infall; reincorporation", "Cooling: hot → cold gas", "Enrichment and ejection"], "galaxy")
    d.box("stars", 35, 465, 315, 100, "Star formation", ["Disk star formation and merger bursts", "Stellar populations and recycling"], "galaxy")
    d.box("bh", 435, 225, 285, 110, "Black holes and AGN", ["Hot- and cold-mode accretion", "Enabled radiative sources", "Radio-mode heating"], "galaxy")
    d.box("rad", 435, 465, 285, 100, "Escaped radiation", ["Ionizing stellar and AGN photons", "X-rays when enabled"], "grid")
    d.box("igm", 810, 465, 285, 100, "IGM evolution", ["Hydrogen ionization", "Thermal and radiation history"], "grid")
    d.edge("halo","gas")
    d.edge("gas","stars")
    d.edge("gas","bh","e","w",dashed=True)
    d.edge("stars","rad","e","w")
    d.edge("bh","rad")
    d.edge("rad","igm","e","w")
    d.edge("stars","gas","w","w",via=[(12,515),(12,280)],color=COLORS["feedback"][0],dashed=True)
    d.label(200, 400, "Stellar feedback and recycled material")
    d.edge("igm","gas","n","n",via=[(952.5,155),(192.5,155)],color=COLORS["feedback"][0],dashed=True)
    d.label(640, 145, "UVB history suppresses infall in later snapshots")
    d.label(560, 635, "Physical connections; execution order is given in the workflow diagram.")
    d.save("galaxy-physics.svg")


def igm_flow():
    d = Diagram(1120, 625, "IGM and 21-cm calculation", "Prepared source and density grids undergo an optional thermal step and ionization before brightness and separately enabled derived products.")
    d.box("prepared", 35, 25, 280, 95, "Prepared grids", ["Galaxy radiation sources", "Simulation density contrast"], "grid")
    d.box("thermal", 410, 25, 300, 110, "Thermal evolution", ["ComputeTs() when enabled", "T_K; x_e; Lyα coupling; T_S"], "grid", True)
    d.box("ion", 805, 25, 280, 110, "Ionization", ["find_HII_bubbles()", "xH; recombination history", "Persistent UVB fields"], "grid")
    d.box("brightness", 805, 250, 280, 110, "21-cm brightness", ["ComputeBrightnessTemperatureBox()", "delta_T", "When enabled"], "grid", True)
    d.box("ps", 410, 450, 300, 100, "Power spectrum", ["Compute_PS()", "k_bins; PS_data; PS_error"], "output", True)
    d.box("lc", 805, 450, 280, 100, "Lightcone", ["ConstructLightcone()", "LightconeBox; lightcone-z"], "output", True)
    d.edge("prepared","thermal","e","w")
    d.edge("thermal","ion","e","w")
    d.edge("prepared","ion","s","n",via=[(175,185),(770,185),(770,0),(945,0)],dashed=True)
    d.label(455, 176, "Thermal step disabled")
    d.edge("ion","brightness")
    d.edge("brightness","ps","s","n",via=[(945,400),(560,400)])
    d.edge("brightness","lc")
    d.label(735, 604, "Power spectrum and lightcone consume the same brightness field; enabled independently.")
    d.save("igm-flow.svg")


def output_tree():
    d = Diagram(1180, 730, "Meraxes output hierarchy", "The master file links snapshot groups. Each snapshot links rank galaxy catalogues, grid products and distribution-function summaries.")
    d.box("master", 440, 20, 300, 85, "meraxes.hdf5", ["Master assembled by rank 0", "After the snapshot loop"], "output")
    d.box("meta", 20, 20, 320, 105, "Master metadata", ["InputParams; Units", "HubbleConversions; gitdiff", "Attributes hold saved metadata"], "input")
    d.box("snaps", 845, 20, 315, 85, "Snapshot groups", ["SnapNNN", "Selected output snapshots"], "output")
    d.box("snap", 430, 205, 320, 95, "Snap", ["Redshift; LTTime; NGalaxies", "Links to the snapshot products"], "output")
    d.box("core", 20, 395, 320, 90, "Core<rank>", ["One group per writing MPI rank", "External links into rank files"], "output")
    d.box("grids", 430, 395, 320, 90, "Grids", ["External link to the grid file", "Distributed spatial products"], "grid")
    d.box("summaries", 840, 375, 320, 120, "Distribution functions", ["HMF; SMF; OIIILF; QuasarLF", "Optional UV and X-ray luminosity functions", "Direct links to rank-0 summaries"], "output")
    d.box("galdata", 20, 570, 320, 100, "Rank datasets", ["Galaxies: compound records", "Tree-index arrays when enabled", "Build-dependent fields"], "output")
    d.box("griddata", 430, 570, 320, 100, "Grid datasets and attributes", ["Source, thermal and ionization cubes", "21-cm arrays and scalar summaries", "Runtime-dependent products"], "grid")
    d.edge("master","meta","w","e")
    d.edge("master","snaps","e","w")
    d.edge("snaps","snap","s","n",via=[(1002.5,160),(590,160)])
    d.edge("snap","core","s","n",via=[(590,340),(180,340)])
    d.edge("snap","grids")
    d.edge("snap","summaries","s","n",via=[(590,340),(1000,340)])
    d.edge("core","galdata")
    d.edge("grids","griddata")
    d.label(590, 715, "Snap is generic notation; stored group names carry a zero-padded snapshot number.")
    d.save("output-tree.svg")


if __name__ == "__main__":
    workflow()
    source_flow()
    galaxy_physics()
    igm_flow()
    output_tree()
