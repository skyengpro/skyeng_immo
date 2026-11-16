# SkyEng Immo

Domain model for property management that PropMS does not provide:

| DocType | Purpose |
|---|---|
| `Occupant` | Who actually lives in a unit - identity, piece d'identite, dates d'entree/sortie |
| `Visitor Log` | Registre des visiteurs pour la guerite: entree/sortie, identite, hote, vehicule |

PropMS models the *lease* (one Customer per unit). It has no notion of the
people in the unit, so access control and gate registers are impossible on it
alone. This app adds that layer without modifying PropMS.

## Sky Immo: the landlord and tenant app

A simple app, on phone, tablet and desktop, where landlords and tenants follow what
staff record in the PropMS desk (scope: [doc/EP-01-landlord-tenant-app.md](doc/EP-01-landlord-tenant-app.md)).
It is served by the site at **`/sky-immo`** (old `/mon-immo` links redirect there). French and English.
Staff open it from the **Sky Immo** icon on the desk's apps screen (or the sidebar's *Applications* menu).

| Who | Role | Sees in the app |
|---|---|---|
| Staff | System Manager / Property Manager | Landlord screens over every property, grouped by landlord |
| Landlord | `Landlord` (no desk access) | Properties whose `unit_owner` is their Customer, and the units below them |
| Tenant | `Tenant` (no desk access) | Their leases, invoices, receipts; reports a problem with a photo |

The app is read-only, apart from the tenant's maintenance request (an ERPNext `Issue`).
Landlords and tenants have no permission on any doctype: everything goes through
`skyeng_immo/sky_immo/api.py`, which filters by the signed-in user (`sky_immo/access.py`).

### Give someone access (desk)

1. Data entry rules, checked on save: every **Property** has a `unit_owner` (use the
   company's own Customer for its own properties); a **Lease** has a single Customer,
   used as tenant and as payer on every lease line.
2. Open the landlord's or tenant's **Customer** › **Sky Immo access**: choose *tenant* or
   *landlord*, the email and the language. This creates the account, links it in the
   Customer's *Portal Users*, and sends Frappe's invitation email. The link lets the person
   choose a password; Frappe then opens the app.

Needs an outgoing **Email Account**. Without one, the account is still created and the
desk says the invitation could not be sent; click again once email is set up.

### Emails

| Email | When | To |
|---|---|---|
| Invitation | Account created from the Customer form | The person |
| Due reminder | Daily, 5 days before an unpaid rent invoice is due | Tenant accounts (or the Customer's email) |
| Receipt (PDF attached) | A Payment Entry against a rent invoice is submitted | Tenant |
| Payment notice | Same | Each landlord, about their own invoices only; property managers for the company's own properties |

Wording is in the Email Templates `Sky Immo - … (fr|en)`, editable in the desk. Each
person gets the email in their account's language.

### Build and develop

`bench build --app skyeng_immo` builds the frontend (`frontend/`, React + Vite) into
`skyeng_immo/public/sky-immo` and writes `skyeng_immo/www/sky-immo/index.html`. Both are
build output and not committed.

```bash
cd apps/skyeng_immo/frontend
npm install
FRAPPE_SITE=immo.localhost npm run dev   # http://localhost:8080/sky-immo, API proxied to the bench on :8001
npm run check:i18n                       # fr.json and en.json complete
```

### Tests and demo data

```bash
CI=1 bench --site <site> run-tests --module skyeng_immo.sky_immo.test_sky_immo
bench --site <site> execute skyeng_immo.sky_immo.demo.create_demo_data   # developer_mode sites only
bench --site <site> execute skyeng_immo.sky_immo.demo.delete_demo_data
```

The tests build a site with two landlords and check that neither sees the other's
properties, leases, invoices, receipts or payment notices. The demo data creates two
landlords and three tenants; the accounts are listed in `sky_immo/demo.py` (password `demo1234`).
