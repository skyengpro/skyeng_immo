**EP-01: Landlord and tenant app on top of PropMS**

**Goal**

Landlords and tenants get one app, on phone, tablet and web, to follow what the property manager records in the PropMS desk: properties, leases, invoices and payments. Tenants can also report a maintenance problem. The app serves two operating modes with the same code. In the first, Sky owns an instance and hosts many landlords on it. In the second, a customer owns an instance and runs it for its own properties.

## Operating modes

### Sky owns an instance

Sky runs one site for many independent landlords. Sky staff work in the desk. Landlords and tenants only ever use the app.

| Role | Who | Access | Sees |
| --- | --- | --- | --- |
| System Manager / Property Manager | Sky staff | Desk | Every property on the site |
| Landlord | An owner with one or more properties | App only | Their own properties and everything tied to them |
| Tenant | A person with a lease on the site | App only | The properties on their leases |

Work specific to this mode:

- All landlords sit under a single ERPNext company, Sky's. Each landlord is a Customer with their own landlord account, and owns their properties through `unit_owner`.
- Sky needs a procedure to onboard a new landlord: Customer, properties, leases, then app accounts for the landlord and the tenants. It starts as a manual checklist.
- Many landlords share one database, so their separation depends entirely on the app. Every screen is checked on a site with two landlords, and neither may see the other's data.

### A customer owns an instance

A property company, or an owner with several buildings, gets its own site and runs it with its own staff.

| Role | Who | Access | Sees |
| --- | --- | --- | --- |
| System Manager / Property Manager | The customer's staff | Desk and app | Every property on the site |
| Landlord | A third-party owner whose properties the customer manages | App only | Their own properties and everything tied to them |
| Tenant | A person with a lease on the site | App only | The properties on their leases |

Work specific to this mode:

- A Property Manager who opens the app gets the landlord screens over every property on the site. When the customer manages properties for third parties, the list is grouped by landlord.
- Each customer gets its own site, deployed through Press.

## Shared by both modes

- One app and one login for every role. The role of the person who signs in decides the home screen and the data shown.
- An account is linked to one or several properties. Properties keep the tree PropMS already uses (building, then units), and access to a building covers its units.
- Who sees what comes down to three rules:

| Role | Properties visible |
| --- | --- |
| System Manager / Property Manager | All properties on the site |
| Landlord | Properties whose `unit_owner` is the landlord's Customer, with their units |
| Tenant | Properties on the tenant's leases |

- Landlords and tenants read data only through app endpoints filtered by the signed-in user. They get no direct access to PropMS or ERPNext doctypes.
- All management stays in the desk: properties, leases, tenants, payments, accounts. The app is read-only, apart from the tenant's maintenance request.
- Staff create accounts in the desk. The person gets an invitation by email.
- Staff record each payment received in the desk as a Payment Entry. The app then shows the invoice as paid, with its receipt.
- French and English.
- Phone first, and the same app runs on tablet and in a desktop browser.

## Screens

### Landlord

A Property Manager in the app sees the same screens over all properties.

1. **Home:** number of properties and tenants, amount collected this month, total unpaid, list of overdue invoices.
2. **My properties:** the property tree by building. Each unit shows its status, current tenant and rent.
3. **Property:** current lease and tenants with their move-in date, deposit, rent schedule, invoices paid and outstanding, past leases.
4. **Tenant:** lease terms, payment history with dates and amounts, invoices still due, invoice download.
5. **Account:** language.

### Tenant

1. **Home:** balance due, next due date, latest maintenance request.
2. **My lease:** unit, lease dates, rent and payment frequency, deposit, rent schedule with the status of each line.
3. **Invoices and receipts:** to pay and paid, invoice detail, download of invoices and receipts.
4. **Maintenance:** new request with a photo, and the list of requests with their status.
5. **Account:** language.

### Emails

Configured in ERPNext, with no screen of their own:

- invitation to a new account;
- reminder to the tenant before a due date;
- receipt to the tenant when a payment is recorded;
- notice to the landlord when a payment is recorded.

## Desk setup

Configuration only, no code:

- a ready-made company template (minimal chart of accounts, "Rent" and "Charges" items);
- automatic submission of invoices in PropMS settings, so invoices have a paid or unpaid status;
- an outgoing email account and the notifications listed above.

Data entry rules, checked by `skyeng_immo` on save:

- a lease has a single Customer, used as tenant, meter payer and on every lease line;
- `unit_owner` is always set on a property, even when the owner is the company itself.

**Scope**

- Both operating modes described above.
- The roles System Manager / Property Manager, Landlord and Tenant.
- The landlord and tenant screens listed above, on phone, tablet and web, in French and English.
- Account invitations and the four emails.
- Tenant maintenance requests with a photo.

**Out of scope**

- Online payment. The payment design is not decided yet.
- Per-property manager and coordinator roles. System Manager and Property Manager cover staff access for now.
- Any landlord action: recording payments, adding tenants, editing leases.
- Owner statements, management fees and payouts to landlords.
- Landlord view of maintenance requests, and tenant feedback on a resolved request.
- Meters, insurance, checklists and keys.
- SMS, WhatsApp and push notifications.
- Accounting in the app.

**Definition of done**

- [ ] On a Sky-owned instance with two landlords, each landlord sees only their own properties, tenants, invoices and payments.
- [ ] On a customer-owned instance, a Property Manager sees every property in the app, and a third-party landlord sees only theirs.
- [ ] A tenant sees their lease, schedule, invoices and receipts, and can file a maintenance request with a photo.
- [ ] A payment recorded in the desk appears on the tenant's and the landlord's screens.
- [ ] An account created in the desk receives its invitation and can sign in.
- [ ] The app works on a phone, a tablet and a desktop browser, in French and in English.
