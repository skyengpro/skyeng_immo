"""Catch the DocType JSON mistakes that only surface during a bench install.

A bad field_order or an unknown link target does not fail the image build --
it fails at `install-app`, 40 minutes later. This runs in seconds.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWN = set()
problems = []

paths = sorted(ROOT.glob("skyeng_immo/**/doctype/*/*.json"))
for path in paths:
    data = json.loads(path.read_text())
    if data.get("doctype") != "DocType":
        continue
    OWN.add(data["name"])

for path in paths:
    data = json.loads(path.read_text())
    if data.get("doctype") != "DocType":
        continue
    name = data["name"]

    order = data.get("field_order", [])
    fields = [f["fieldname"] for f in data.get("fields", [])]
    if set(order) != set(fields):
        problems.append(f"{name}: field_order != fields ({set(order) ^ set(fields)})")
    if len(order) != len(set(order)):
        problems.append(f"{name}: duplicate entries in field_order")

    if not data.get("permissions"):
        problems.append(f"{name}: no permissions defined")

    if data.get("module") != "Immobilier":
        problems.append(f"{name}: module is {data.get('module')!r}, expected 'Immobilier'")

    for f in data.get("fields", []):
        if f["fieldtype"] in ("Link", "Table") and not f.get("options"):
            problems.append(f"{name}.{f['fieldname']}: {f['fieldtype']} without options")
        if f.get("reqd") and f.get("read_only") and not f.get("default"):
            problems.append(f"{name}.{f['fieldname']}: reqd + read_only with no default")

    title = data.get("title_field")
    if title and title not in fields:
        problems.append(f"{name}: title_field {title!r} is not a field")

print(f"checked {len(OWN)} doctypes: {', '.join(sorted(OWN))}")
if problems:
    print("\n".join("FAIL " + p for p in problems))
    sys.exit(1)
print("all doctype JSON valid")
