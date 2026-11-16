
# ADR-xxx: Sky-immo, a landlord and tenant app on PropMS

| Status           | Proposed                               |
| ---------------- | -------------------------------------- |
| Date             | 2026-11-16                             |
| Deciders         | Platform Engineering                   |
| Affected systems | Every site where Sky-immo is installed |
| Status           | Proposed                               |

## Context

PropMS is a property management app built on ERPNext. It manages properties, leases, rent schedules, invoicing and property deposits. Everything happens in the administration interface (Desk), which is reserved for the property manager. PropMS provides no interface for landlords or tenants.

We need a mobile app, also usable on a tablet or a computer, that lets a customer who owns a property follow their properties. They must be able to see the condition of each property, know who occupies each unit and since when, and consult the leases and the history of invoices and payments.

The app must also let a tenant, bound by a lease to a registered property, consult the properties they occupy (they may occupy several) and their details: lease, rent, deposit and schedule. The tenant must be able to find their payment history and invoices, and to submit a maintenance request from their own space and follow it.

## Options considered

- A separate app that builds on PropMS: chosen. PropMS stays unchanged, and the app adds only the easy-to-use interface that landlords and tenants need. It is still one more app to build and maintain.
- PropMS as is: rejected. Its interface is designed for the property manager, not for tenants or landlords.
- A property app developed outside the Frappe ecosystem: rejected. Leases, schedules, invoicing and deposits, which PropMS already provides, would have to be rebuilt.

## Decision

Sky-immo is a separate app, installed on the same site as PropMS and ERPNext. It uses their data without changing their code.

1. Management stays in the administration interface: properties, leases, tenants, invoices and payments. The app is used for consulting, and for handling maintenance work on a property: the tenant creates a maintenance request and the landlord approves or rejects it.
2. One app and one sign-in serve every role. The property manager sees every property on the site, the landlord the properties they own, and the tenant the units on their leases.
3. The same app serves both operating modes described below.

### Operating modes

Mode A, "Sky owns an instance". Sky hosts and administers a site shared by several landlords, all of whom are customers of the Sky company. Landlords and tenants have access to the app only, and each sees only the properties they are linked to.

Mode B, "A customer owns an instance". A customer who owns several properties, or who runs their own agency, has their own site. They administer their properties themselves and also use the app, where they sign in as the owner to follow the properties they own, the current leases and the tenants. If this customer has tenants, those tenants can use the same app to sign in and follow their leases.

> **Diagram : screens, mode A.** [doc/screens-immo-mode-a.mermaid](doc/screens-immo-mode-a.mermaid).

> **Diagram : screens, mode B.** [doc/screens-immo-mode-b.mermaid](doc/screens-immo-mode-b.mermaid).

> **Diagram : functional sequences.** [doc/app-usage-flows-immo.md](doc/app-usage-flows-immo.md).

## Consequences

* Landlords and tenants follow their properties, leases and invoices from a phone, a tablet or a computer. The property manager keeps the administration interface and all of PropMS.
* Lease, rent and invoicing logic stays in PropMS and ERPNext, and benefits from their fixes.
* The data stays in PropMS and ERPNext, with no copy. Online payment can be added later on the same data.
* One app covers both modes and provides an easy-to-use interface.
* Sky-immo depends on a third-party app. Each PropMS update must be tested against every flow before it reaches a site.
* In mode A, landlords share the same database. Their separation rests entirely on the app's access rules.
* What landlords and tenants see depends on what staff enter in the administration interface: the right owner on each property, the right tenant on each lease.
* PropMS has no landlord approval for maintenance requests. The app adds it and must keep it consistent with the requests the property manager sees.

## Implementation

| Order | Step                                                                   | Ticket |
| ----- | ---------------------------------------------------------------------- | ------ |
| 1     | App foundation, roles and settings                                     | -      |
| 2     | Sign-in, invitations and access rules for each role                    | -      |
| 3     | Landlord screens, including maintenance approval, also used in mode B  | -      |
| 4     | Tenant screens, including the maintenance request and its closure      | -      |
| 5     | Tests: two landlords on one site, and every flow on each PropMS update | -      |
