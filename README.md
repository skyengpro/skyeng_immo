# SkyEng Immo

Landlord and tenant app on top of ERPNext and PropMS (Frappe v16).

Staff keep managing landlords, properties, leases, tenants and payments in the desk. This app gives
landlords and tenants their own interface on the same site:

- **Landlord**: their properties and units, tenants, invoices, and approval of maintenance requests.
- **Tenant**: their units, leases, invoices and receipts, and maintenance requests.

It works in two modes: Sky owns the instance (mode A), or a customer owns it (mode B). The mode of
a site is set in **Sky Immo Settings** (System Manager and Property Manager only).

## Sky-immo app

Served at `/sky-immo` on the same site (Vue 3 + frappe-ui, in `frontend/`). It is built by
`bench build` and can be added to a phone's home screen. Roles `Landlord` and `Tenant` have no Desk
access. Interface in English and French.

## Documentation

- [`doc/app-usage-flows-immo.md`](doc/app-usage-flows-immo.md): roles, onboarding, invoicing,
  maintenance and per-role flows.
- `doc/screens-immo-mode-a.mermaid` / `.pdf` and `doc/screens-immo-mode-b.mermaid` / `.pdf`: the
  screens to build.

## Requirements

Frappe, ERPNext and PropMS on `version-16`. PropMS is not modified by this app.

### Tested versions

CI runs against these exact commits, pinned in `.github/workflows/ci.yml`. Check out the same
commits on a local bench to reproduce a CI run.

| App | Branch | Version | Commit | Date |
| --- | --- | --- | --- | --- |
| [frappe](https://github.com/frappe/frappe) | `version-16` | 16.60.2 | `2df0425571ebbaed878eabc3edc5b7e7c3327ae0` | 2026-11-18 |
| [erpnext](https://github.com/frappe/erpnext) | `version-16` | 16.60.0 | `886ab6ae187244e7f1b852393384ab6019d56264` | 2026-11-17 |
| [propms](https://github.com/Aakvatech-Limited/PropMS) | `version-16` | 16.1.0 | `554593643564f6e71cbfe1b22787ecb198f9183c` | 2026-10-11 |
| [payments](https://github.com/frappe/payments) | `version-16` | 0.0.1 | `cca07d9f9392e2ea0e521c5975151db9e4b6c321` | 2026-05-26 |

The app takes no payment and `payments` is not in `required_apps`. The test suite needs it because
ERPNext's Payment Gateway Account links to its Payment Gateway, and Frappe's test record generator
follows every link.

PropMS commits from 2026-11-14 onwards are not supported yet. They make `Property.status` a link to
Property Status and create those records only in a patch, which a fresh install skips, so a new site
cannot save a property. Bump all pins together after a green run on a fresh local site.
