# skyeng_immo

Frappe app that adds the property-management layer PropMS does not provide: the people in a unit
(`Occupant`), the gate register (`Visitor Log`), `Vehicle` and `Parking Space`, plus warranty and
unit link on ERPNext `Asset`. Targets Frappe v16 (frappe, erpnext and propms on `version-16`).
ERPNext and PropMS are required (`required_apps` in `hooks.py`). Earlier versions are out of scope.

## Source of truth

When sources disagree, follow this order:

1. Design docs in `doc/` (usage flows, screens) and ADRs once they exist
2. Installed source of frappe, erpnext, propms (see "Method")
3. Community skills `.claude/skills/frappe-*` (generic, not written for this app)
4. Your own recollection

If a task would contradict a documented decision, stop and say so; never deviate silently.

## Layout

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
- `scripts/validate_doctypes.py`: DocType JSON sanity check (field_order, link targets).
- `scripts/check_packaging.py`: packaging guard.

## Invariants (never break)

1. PropMS is never modified. This app extends it (links to `Property` / `Lease`), it does not patch it.
2. `frappe`, `erpnext`, `propms` are never pip dependencies in `pyproject.toml`: uv would resolve the
   framework and the Press build dies with exit 167. `[tool.bench.frappe-dependencies]` is fine.
3. Fixtures are explicit allowlists by name. Never a broad filter (e.g. `is_public = 1`): it would
   make this app own and overwrite ERPNext's built-in cards and charts on every migrate.
4. A fresh install yields a working app: roles, custom fields and dashboard ship in code or fixtures,
   never as hand-configured site data.
5. Asset custom fields degrade gracefully when `Asset` is absent.
6. Personal data (occupant identity, ID documents, visitor names, plates) never in logs, fixtures,
   tests or commit messages. Tests use obviously fake data.

## Frappe rules

- No `frappe.db.commit()` in controllers or hooks.
- Deliverables are app code. No Server Scripts, no Client Scripts created in the desk.
- Code must work on v16. Check APIs in the installed v16 sources.

## Method

- **Don't reinvent.** Before adding a helper or doctype, search `frappe`, `erpnext`, `propms` for it.
  State what exists and the specific limit that blocks reuse. Installed sources are readable through
  `additionalDirectories` (`.claude/settings.json`).
- **Verify version-sensitive APIs in source, not in a skill or from memory.** Known case: the
  community skill `frappe-core-cache` teaches `frappe.lock()`, which does not exist in v16. Cite the
  file you checked.

## Commands

```bash
bench --site <dev-site> run-tests --app skyeng_immo   # site tests
pre-commit run --all-files                            # hygiene, ruff, gitleaks (staged)
python scripts/validate_doctypes.py                   # DocType JSON check
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
PRs target `develop`. Behaviour change => update the matching doc in `doc/` in the same PR.

## Done means

Site tests green, linters green (pre-commit, static checks, gitleaks, semgrep), docs updated, and the
invariants above checked on the diff.
