# Property app usage flows

This document describes how each role uses the app in the two operating modes defined in EP-01. The screens to build are shown separately, in `screens-immo-mode-a.mermaid` and `screens-immo-mode-b.mermaid`.

Online payment is not covered. Until it is designed, the property manager records each payment received (cash, bank transfer, MoMo outside the app) in the desk.

## Roles and access

| Role                              | Mode A: Sky owns an instance          | Mode B: A customer owns an instance                                                         |
| --------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------- |
| System Manager / Property Manager | Sky staff. Desk only.                 | The customer's staff. Desk and app.                                                         |
| Landlord                          | Every landlord on the site. App only. | A third-party owner whose properties the customer manages. App only. This role is optional. |
| Tenant                            | App only.                             | App only.                                                                                   |

In both modes, one app serves every role. The role of the signed-in person decides the home screen and the properties shown:

- the property manager sees every property on the site;
- the landlord sees the properties they own (`unit_owner`), with their units;
- the tenant sees the units on their leases. A tenant can occupy more than one unit.

A person who is both landlord and tenant gets both spaces and switches between them from the account menu.

After sign-in, a landlord or a tenant opens the app. The property manager opens the app in mode B and the desk in mode A. In mode A, `/sky-immo` sends the property manager to the desk.

Management happens in the desk: landlords, properties, leases, tenants, accounts and payments. The app has two actions, both about maintenance: the tenant creates a request and marks it completed, and the landlord approves or rejects it.

## 1. Onboarding

### 1.1 Mode A: Sky onboards a landlord

Landlords have no instance of their own. Sky staff register them on the Sky site, under Sky's single company.

```mermaid
sequenceDiagram
    autonumber
    actor S as Sky staff (desk)
    participant D as Sky site
    actor B as Landlord
    actor L as Tenant

    S->>D: Creates the landlord (Customer)
    S->>D: Creates their properties in the tree (building, then units), with the landlord as owner
    S->>D: Creates each lease, with its tenant, units, rent and schedule
    S->>D: Invites the landlord and each tenant from their Customer (section 1.3)
    D-->>B: Invitation email
    D-->>L: Invitation email
    B->>D: Opens the link and sets a password
    D-->>B: The app opens on their properties
    L->>D: Opens the link and sets a password
    D-->>L: The app opens on their units
    Note over S,L: A second landlord follows the same path on the same site. Neither sees the other's properties.
```

Onboarding starts as a manual checklist for Sky staff.

### 1.2 Mode B: the customer sets up its instance

The customer gets its own site. Its staff enter its properties. If the customer also manages properties for third-party owners, it can give them landlord access.

```mermaid
sequenceDiagram
    autonumber
    actor G as Customer staff (desk)
    participant D as Customer site
    actor B as Third-party landlord
    actor L as Tenant

    G->>D: Creates its properties in the tree, with the customer's company as owner
    opt Properties managed for a third-party owner
        G->>D: Creates the third-party landlord (Customer) and links their properties
        G->>D: Invites the third-party landlord (section 1.3)
        D-->>B: Invitation email
    end
    G->>D: Creates each lease, with its tenant, units, rent and schedule
    G->>D: Invites each tenant (section 1.3)
    D-->>L: Invitation email
    L->>D: Opens the link and sets a password
    D-->>L: The app opens on their units
```

The owner is always set on every property, even when it is the customer's own company. Visibility rules therefore stay the same in both modes.

### 1.3 Invitation

Staff invite a person from the desk: they open the Customer and click **Invite to Sky-immo**.

- **Who can invite:** System Manager and Property Manager. A Property Manager also needs a role that can read Customer, such as Sales User, because PropMS gives them no access to it.
- **What the Customer needs:** an email address on the primary contact, and at least one property owned (a unit without an owner takes the owner of its nearest parent) or one active lease. The site also needs an outgoing email account.
- **What happens:** the user is created, or reused if the email already has one, and added to the Customer's Portal Users. They get Landlord if the Customer owns a property and Tenant if the Customer has an active lease. They receive an email with a link to choose a password, and the app opens after sign-in.
- **What does not happen:** the ERPNext Customer role is not given, so the ERPNext portal stays closed to them. A disabled user is refused until staff enable them. A staff member keeps their desk access and their default app.
- **Inviting again:** sends a new link and changes nothing else.

## 2. Invoicing and payment (both modes)

PropMS generates invoices from each lease's schedule. The property manager records payments received. The app only shows the result.

```mermaid
sequenceDiagram
    autonumber
    participant D as Site
    actor G as Property manager (desk)
    actor L as Tenant
    actor B as Landlord

    D->>D: On the schedule date, generates the invoice and submits it
    D-->>L: Reminder email a few days before the due date
    alt The tenant pays
        L->>G: Pays outside the app (cash, transfer, MoMo)
        G->>D: Records the payment against the invoice
        D-->>L: Receipt by email
        D-->>B: Payment notice by email
        Note over L,B: In the app, the invoice shows as paid and the receipt can be downloaded.
    else No payment by the due date
        Note over D,B: The invoice stays unpaid. It appears in overdue invoices on the landlord's home and in the tenant's balance due.
    end
```

In mode B, a landlord exists only for properties managed for a third party. For the customer's own properties, the payment notice goes to the property manager.

## 3. Maintenance request: Issue in ERPNext (both modes)

A request goes through four statuses. The tenant opens it, the landlord decides, and the tenant closes it once the work is done.

| Status            | Set by                | Meaning                            |
| ----------------- | --------------------- | ---------------------------------- |
| Awaiting approval | Tenant, on creation   | The landlord has not decided yet   |
| In progress       | Landlord, on approval | The work is accepted and under way |
| Rejected          | Landlord              | The work will not be done          |
| Completed         | Tenant                | The work is done                   |

```mermaid
sequenceDiagram
    autonumber
    actor L as Tenant
    participant A as App
    participant D as Site
    actor B as Landlord

    L->>A: Creates a request on one of their units, with a photo
    A->>D: Records it as "Awaiting approval"
    D-->>B: The request appears on the landlord's home and in their maintenance list
    B->>A: Opens the request: unit, tenant, description, photo
    alt The landlord approves
        B->>A: Approves, with an optional message for the tenant
        A->>D: Status "In progress"
        D-->>L: The tenant sees "In progress" and the landlord's message
        Note over L,B: The work is organised outside the app.
        L->>A: Marks the request as completed once the work is done
        A->>D: Status "Completed"
        D-->>B: The landlord sees "Completed"
    else The landlord rejects
        B->>A: Rejects, with an optional message for the tenant
        A->>D: Status "Rejected"
        D-->>L: The tenant sees "Rejected" and the landlord's message
    end
    Note over D: Staff see every request in the desk, whatever its status.
```

With the decision, the landlord can leave the tenant a message of up to 250 characters. It is kept on the request (`sky_immo_decision_note`, with `sky_immo_decided_by` and `sky_immo_decided_on`) and shown on both sides: "Your answer" for the landlord, "Answers from the landlord" for the tenant. The tenant does not see the landlord's name. The request is not a conversation: there is one answer, given with the decision.

Only a user linked to the owner of the property decides: a portal user of the Customer set as `unit_owner` on the property or on its nearest parent. In mode B, the customer's own properties have the customer's own Customer as owner, so a property manager decides on them by being a portal user of that Customer.

## 4. Landlord (both modes)

The landlord consults their properties and tenants, and decides on maintenance requests. They record no payment, tenant or lease.

```mermaid
sequenceDiagram
    autonumber
    actor B as Landlord
    participant A as App
    participant D as Site

    B->>A: Signs in
    A->>D: Asks for visible properties
    D-->>A: Landlord role: their properties and units
    A-->>B: Home: properties, tenants, collected this month, total unpaid, occupancy, overdue invoices, maintenance awaiting approval and in progress
    B->>A: Opens "My properties"
    A-->>B: Tree by building. For each unit: status, tenant, rent
    B->>A: Opens a property
    A-->>B: Current lease, tenants and move-in date, deposit, schedule, invoices, past leases, maintenance on this property
    B->>A: Opens "Tenants"
    A-->>B: Every tenant, current or former, with the unit they occupy or occupied
    B->>A: Opens a tenant
    A-->>B: Lease terms, payments (dates and amounts), invoices still due
    B->>A: Downloads an invoice
    A-->>B: Invoice PDF
    B->>A: Opens "Maintenance"
    A-->>B: Requests on their properties, by status. Approval as in section 3
    Note over B,D: From the home screen, an overdue invoice opens the tenant concerned, and a pending request opens that request.
```

## 5. Property manager in the app (mode B)

In mode B, the customer's staff can open the app to check their properties away from the office. They see the same screens as the landlord, over every property on the site.

```mermaid
sequenceDiagram
    autonumber
    actor G as Customer property manager
    participant A as App
    participant D as Customer site

    G->>A: Signs in with their desk account
    A->>D: Asks for visible properties
    D-->>A: Property Manager role: every property on the site
    A-->>G: Home: totals across all properties, including maintenance
    G->>A: Opens "My properties", "Tenants" or "Maintenance"
    A-->>G: Same lists as for the landlord. Properties and tenants of the customer's own Customer apart from those of third-party landlords, grouped by landlord
    G->>A: Approves or rejects a request on one of the customer's own properties (as a portal user of the customer's Customer)
    A->>D: Status updated
    Note over G,D: Anything else is changed in the desk, with the same account.
```

In mode A, Sky staff work in the desk and do not need the app.

## 6. Tenant (both modes)

The tenant consults their units, leases and invoices, and reports problems in their home.

```mermaid
sequenceDiagram
    autonumber
    actor L as Tenant
    participant A as App
    participant D as Site

    L->>A: Signs in
    A->>D: Asks for their leases
    D-->>A: Tenant role: their units and leases
    A-->>L: Home: units occupied, balance due, next due date, latest maintenance request
    L->>A: Opens "My properties"
    A-->>L: Every unit they occupy: building, unit, what it is (type, bedrooms, area), rent, lease end
    L->>A: Opens a unit
    A-->>L: Unit details (type, rooms, area, parking, furnished, smoking, amenities, description), lease dates, rent and frequency, deposit, schedule with the status of each line
    L->>A: Opens "Invoices and receipts"
    A-->>L: Invoices to pay and paid, across all their units
    L->>A: Downloads an invoice or a receipt
    A-->>L: PDF
    L->>A: Opens "Maintenance"
    A-->>L: Their requests and their status. New request and completion as in section 3
```

## 7. What differs between modes

| Point                       | Mode A                                  | Mode B                                                                              |
| --------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------- |
| Who runs the desk           | Sky staff                               | The customer's staff                                                                |
| ERPNext company             | A single one, Sky's, for every landlord | The customer's                                                                      |
| Landlords                   | Every owner on the site                 | Third-party owners only, if any                                                     |
| Property manager in the app | No                                      | Yes, over every property, grouped by landlord                                       |
| Who approves maintenance    | The landlord                            | The user linked to the owner: the third-party landlord, or for the customer's own properties a property manager who is a portal user of the customer's Customer |
| Landlord and tenant screens | Identical                               | Identical                                                                           |
| Landing page of the property manager | The desk                       | The app                                                                             |
