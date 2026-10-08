project = "Meraxes"
author = "Meraxes developers"

extensions = ["myst_parser", "sphinx.ext.mathjax", "sphinx_rtd_theme"]
source_suffix = {".md": "markdown"}
root_doc = "index"

myst_enable_extensions = ["dollarmath", "amsmath"]
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
