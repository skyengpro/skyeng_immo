# skyeng_immo

Frappe app that gives landlords and tenants their own interface on top of ERPNext and PropMS. PropMS
and the desk stay the back office: staff manage landlords, properties, leases, tenants, accounts and
payments there. This app adds the **landlord and tenant app** (epic EP-01), served from the same
site. Targets Frappe v16 (frappe, erpnext and propms on `version-16`). ERPNext and PropMS are
required (`required_apps` in `hooks.py`). Earlier versions are out of scope.

## Source of truth

When sources disagree, follow this order:

1. Design docs in `doc/` and ADRs once they exist:
   - `doc/app-usage-flows-immo.md`: roles, onboarding, invoicing, maintenance, per-role flows.
   - `doc/screens-immo-mode-a.mermaid` / `.pdf` and `doc/screens-immo-mode-b.mermaid` / `.pdf`:
     the screens to build, per mode.
2. Installed source of frappe, erpnext, propms (see "Method")
3. Community skills `.claude/skills/frappe-*` (generic, not written for this app)
4. Your own recollection

If a task would contradict a documented decision, stop and say so; never deviate silently.
If the docs are silent on a point, ask instead of guessing.

## What we are building

One app serves every role. The signed-in person's role decides the home screen and the data shown.

| Role | Sees | Can do in the app |
| --- | --- | --- |
| Landlord | Properties they own (`unit_owner`), their units, tenants, leases, invoices | Approve or reject maintenance requests |
| Tenant | Units on their leases (possibly several), leases, invoices, receipts | Create a maintenance request, mark it completed |
| Property Manager (mode B only) | Every property on the site, grouped by landlord | Same screens as the landlord, over the whole site |

Screens, for both modes: Home, My properties, Property, Tenants and Tenant (landlord side),
Invoices and receipts (tenant side), Maintenance, Account (language). Landlord and tenant screens are
identical in both modes.

Two operating modes, same code:

- **Mode A**: Sky owns the instance. One company (Sky's), every landlord on the same site, no
  Property Manager in the app. Landlords never see each other's properties.
- **Mode B**: a customer owns the instance. Third-party landlords are optional. For the customer's
  own properties there is no landlord account, so the Property Manager approves maintenance.

The owner is always set on every property, even when it is the customer's own company, so visibility
rules are the same in both modes.

## Scope: what the app does NOT do

- No payment recording and no online payment. Staff record payments in the desk (cash, transfer,
  MoMo outside the app). The app only shows invoice status and downloads invoices and receipts.
- No creation or editing of landlords, properties, leases, tenants or accounts. That is the desk.
- Maintenance is the only write path: tenant creates and completes, landlord approves or rejects.
  Statuses: `Awaiting approval` -> `In progress` or `Rejected` -> `Completed`. The work itself is
  organised outside the app.

## Layout

- `skyeng_immo/`: the Frappe app (`hooks.py`, `install.py`, `modules.txt`, `patches/`).
- `doc/`: functional docs and screens. Behaviour change => update the matching doc in the same PR.
- Module `Immobilier`: doctypes `Occupant`, `Visitor Log`, `Vehicle`, `Parking Space`
  (`skyeng_immo/immobilier/doctype/`).
- `install.py`: roles (`Gardien`, `Property Manager`, `Technicien`) and Asset custom fields,
  run on `after_install` and `after_migrate`. Must stay idempotent. `before_uninstall` drops the
  Asset custom fields.
- `fixtures/`: roles `Landlord` and `Tenant` (`desk_access = 0`, restored on every migrate), then
  Number Cards, Dashboard Charts, Reports, Workspace, Workspace Sidebar, Desktop Icon of the
  `Immobilier` dashboard. Order in `hooks.fixtures` matters (cards/charts before workspace).
- `Sky Immo Settings` (Single, module `Immobilier`): operating mode of the site. System Manager and
  Property Manager only.
- Landlord and tenant app: Vue 3 + frappe-ui + Vite in `frontend/`, served at `/sky-immo` by
  `www/sky_immo.py` through `website_route_rules`. `bench build` builds it into
  `skyeng_immo/public/frontend/` and `skyeng_immo/www/sky_immo.html` (both gitignored).
- Translations: `skyeng_immo/locale/fr.po` (Frappe gettext), loaded by the frontend from
  `skyeng_immo.api.get_translations`.
- `scripts/check_packaging.py`: CI guard for invariant 2 (no framework package as pip dependency).

## Invariants (never break)

1. PropMS is never modified. This app extends it (reads `Property` / `Lease`), it does not patch it.
2. `frappe`, `erpnext`, `propms` are never pip dependencies in `pyproject.toml`: uv would resolve the
   framework and the Press build dies with exit 167. `[tool.bench.frappe-dependencies]` is fine.
3. Data visibility is enforced **on the server**, by role and ownership (landlord: `unit_owner`;
   tenant: own leases). Hiding something in the UI is never the access control. A landlord must never
   read another landlord's data, a tenant must never read another tenant's.
4. API endpoints check permissions explicitly. No `allow_guest`, no `ignore_permissions` to make a
   screen work; fix the permission model instead.
5. Fixtures are explicit allowlists by name. Never a broad filter (e.g. `is_public = 1`): it would
   make this app own and overwrite ERPNext's built-in records on every migrate.
6. A fresh install yields a working app: roles, custom fields and config ship in code or fixtures,
   never as hand-configured site data. `install.py` hooks must stay idempotent.
7. Personal data (identity, ID documents, names, phone numbers, amounts tied to a person) never in
   logs, fixtures, tests or commit messages. Tests use obviously fake data.

## Frappe rules

- No `frappe.db.commit()` in controllers or hooks.
- Deliverables are app code. No Server Scripts, no Client Scripts created in the desk.
- Code must work on v16. Check APIs in the installed v16 sources.

## Method

- **Don't reinvent.** Before adding a helper, doctype or field, search `frappe`, `erpnext`, `propms`
  for it. State what exists and the specific limit that blocks reuse. Installed sources are readable
  through `additionalDirectories` (`.claude/settings.json`).
- **Verify version-sensitive APIs in source, not in a skill or from memory.** Known case: the
  community skill `frappe-core-cache` teaches `frappe.lock()`, which does not exist in v16. Cite the
  file you checked.
- Check the role and field names the docs rely on (`Landlord`, `Tenant`, `unit_owner`) against the
  installed PropMS before building on them.

## Commands

```bash
bench --site <dev-site> run-tests --app skyeng_immo   # site tests
pre-commit run --all-files                            # hygiene, ruff, gitleaks (staged)
python scripts/check_packaging.py                     # packaging guard
gitleaks git --config .gitleaks.toml --redact .       # full-history secret scan
cd frontend && yarn dev                               # frontend dev server (proxies to bench)
bench build --app skyeng_immo                         # frontend build + compile translations
bench generate-pot-file --app skyeng_immo             # refresh locale/main.pot, then update fr.po
```

Never run `bench migrate`, `restore`, `reinstall` or `drop-site` against a non-dev site.

## Conventions

Code, identifiers, comments, commit messages: English. New user-facing strings are written in
English and translated in `skyeng_immo/locale/fr.po`; the older French labels of the `Immobilier`
doctypes stay as they are.
PRs target `develop`.

## Done means

Site tests green (including a test that one landlord or tenant cannot read another's data), linters
green (pre-commit, packaging guard, gitleaks, semgrep, pip-audit), docs updated, and the invariants
above checked on the diff.
