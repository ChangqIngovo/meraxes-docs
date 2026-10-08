"""Create the equation index from labeled MyST math directives."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = [
    "inputs", "workflow", "galaxy-physics", "black-holes", "igm",
    "stochasticity", "optional-physics", "numerics", "outputs",
]


def collect(path):
    title = None
    heading = "Definitions"
    rows = []
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("# "):
            title = line[2:]
        elif re.match(r"^#{2,6} ", line):
            heading = re.sub(r"^#+ ", "", line)
        if line.startswith("```{math}"):
            block = []
            for item in lines[index + 1:]:
                if item == "```":
                    break
                block.append(item)
            labels = [item.removeprefix(":label:").strip()
                      for item in block if item.startswith(":label:")]
            if len(labels) != 1:
                raise ValueError(f"Expected one math label: {path}:{index + 1}")
            rows.append((labels[0], heading))
        if line.startswith("```"):
            index += 1
            while index < len(lines) and lines[index] != "```":
                index += 1
        index += 1
    return title, rows


def main():
    groups = []
    labels = set()
    for name in PAGES:
        path = DOCS / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(path)
        title, rows = collect(path)
        for label, _ in rows:
            if label in labels:
                raise ValueError(f"Duplicate equation label: {label}")
            labels.add(label)
        groups.append((name, title, rows))
    content = [
        "# Equation index", "",
        f"The guide contains **{len(labels)} numbered equation blocks**. Each entry",
        "links to its definition and surrounding variables, units, activation",
        "conditions, source routine and scientific references. A block may contain",
        "several coupled relations. Equations describe the inspected implementation;",
        "paper-only definitions are identified in their corresponding chapter.", "",
    ]
    for name, title, rows in groups:
        if not rows:
            continue
        content += [f"## {title}", "", f"[Read the chapter]({name}.md).", "",
                    "| Equation | Process | Identifier |", "|---|---|---|"]
        for label, heading in rows:
            heading = heading.replace("|", r"\|")
            content.append(f"| {{eq}}`{label}` | {heading} | `{label}` |")
        content.append("")
    (DOCS / "equations.md").write_text("\n".join(content), encoding="utf-8")
    print(f"Indexed {len(labels)} equation blocks across {len(groups)} chapters")


if __name__ == "__main__":
    main()
