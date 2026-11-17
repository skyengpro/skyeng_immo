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
