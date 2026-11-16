"""Fail if frappe / erpnext / propms are declared as pip dependencies.

uv would then resolve the framework itself, and frappe pins pypika to a git
URL, which uv rejects for anything that is not a direct requirement: the Press
image build dies with exit 167 (see skyengpro/propms commit 8c0b1d8).

Only `[project].dependencies` and optional-dependencies are checked.
`[tool.bench.frappe-dependencies]` is bench metadata, not pip, and is allowed.
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
