"""Fail if frappe, erpnext or propms is a pip dependency in pyproject.toml.

uv would then resolve the framework and the Press build fails with exit 167.
"""

import pathlib
import re
import sys
import tomllib

FORBIDDEN = {"frappe", "erpnext", "propms"}
ROOT = pathlib.Path(__file__).resolve().parent.parent

project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
declared = list(project.get("dependencies", []))
for extra in project.get("optional-dependencies", {}).values():
	declared.extend(extra)

bad = []
for requirement in declared:
	name = re.split(r"[\s<>=!~;\[@]", requirement.strip(), maxsplit=1)[0].lower()
	if name in FORBIDDEN:
		bad.append(requirement)

if bad:
	for requirement in bad:
		print(f"::error file=pyproject.toml::framework package must not be a pip dependency: {requirement}")
	sys.exit(1)

print("packaging OK")
