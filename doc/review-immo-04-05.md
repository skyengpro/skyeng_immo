# Review of IMMO-04 and IMMO-05

Branch: `immo-05-tenant-screens-and-maintenance-requests`, which contains IMMO-04 and IMMO-05.

The reference for this review is the IMMO-04 and IMMO-05 tickets, `doc/app-usage-flows-immo.md`, the screens in `doc/screens-immo-mode-a.mermaid` and `doc/screens-immo-mode-b.mermaid`, and the IMMO-03 base merged in `develop`. Points marked "verified" were reproduced on a test site with the IMMO-03 fixture of two landlords and two tenants (`tests/utils.py::SharedSite`).

The maintenance flow matches the tickets. Approve, reject and complete follow the expected statuses, and Desk shows Rejected as Closed and Completed as Resolved. A unit cannot be saved without an owner, the request limits apply, and a photo returns 403 outside the request's scope. The changes below are needed to bring the branch in line with Sky-immo's rules and screens.

## 1. Two access layers

The branch adds a package `skyeng_immo/sky_immo/` (`access.py`, `api.py`, `invite.py`, a second `set_default_app`) next to IMMO-03's `access.py`, `api.py` and `invitation.py`. The Vue app calls only `sky_immo.api`, so no screen goes through IMMO-03's `get_scope` any more. IMMO-03 requires every endpoint to start from that one scope function.

Requested change: the app endpoints start from `skyeng_immo.access.get_scope`, and `sky_immo/access.py`, `sky_immo/invite.py` and the duplicate `set_default_app` are removed. This fixes points 2.1 to 2.6 at once.

## 2. Data visibility (invariant 3), verified

| # | Problem | Location |
|---|---|---|
| 2.1 | A landlord sees units of another landlord inside their building. Every `lft`/`rgt` descendant is included, even a unit with its own `unit_owner`. Landlord 1 can open unit 1B (landlord 2) and its maintenance request. | `sky_immo/access.py:101-112` |
| 2.2 | Access is also granted through a Contact whose `user` is the account. It must come only from the Customer's Portal Users. | `sky_immo/access.py:58-68` |
| 2.3 | A disabled Customer keeps its access. | `sky_immo/access.py`, `linked_customers` |
| 2.4 | A tenant sees requests on units they never rented. The filter is `customer OR raised_by`, with no condition on the property. | `sky_immo/api.py:400-404` |
| 2.5 | A user who is both Landlord and Tenant gets only one side, because `app_role` returns a single role. IMMO-03 gives the union of both. | `sky_immo/access.py:41-51` |
| 2.6 | The tenant scope depends on the payer (`Lease.customer`, `Sales Invoice.customer`). It must depend on the lease (`Lease.lease_customer`, `Sales Invoice.lease`). | `sky_immo/access.py:131, 152` |

On 2.6, the IMMO-03 rule stands: invoices are found through the lease, whoever the payer is. A property has successive leases with different tenants over the years, and its history must stay complete. The landlord sees every lease, tenant and invoice of the property, past and current. Each tenant sees every invoice of their own leases.

## 3. Other blocking points

Tests. On this branch, every IMMO-03 test class and every Immobilier doctype test fails in `setUpClass`. The new `validate_property` rejects fixture properties that have no owner, and `validate_lease` rejects the IMMO-03 lease whose payer is not the tenant. The fixtures need an owner on each property, and `validate_lease` must not contradict 2.6. The new endpoints also need the two-landlord, two-tenant cases. Such a test would have caught 2.1.

Photos. Only the `data:image/...` prefix is checked, so any content declared as `image/png` is accepted. This was verified with an HTML payload. The content has to be checked before it is written, for example with `PIL.Image.open(...).verify()` or by reading the file signature. Location: `sky_immo/api.py:620`.

`allow_guest=True` on `get_session` breaks invariant 4. The session can come from the boot data in `www/sky_immo.py`, or the endpoint can drop `allow_guest`. Location: `sky_immo/api.py:50`.

Symlink. `skyeng_immo/public/node_modules` is committed as a symlink to the absolute path `/workspace/development/...`. It has to be removed from git.

## 4. Missing screens

Each screen in `screens-immo-mode-a.mermaid` was checked against `frontend/src/router.js`, `nav.js` and the pages.

Landlord:

- Tenants (B4) does not exist. The router and the navigation have no list of current and former tenants with their units, and the "Tenants" card on the home screen links nowhere.
- Home (B1) shows maintenance requests awaiting approval only. The screen also lists those in progress.
- Property (B3) has no maintenance requests for the property and no link to a request. `get_property` returns none.

Tenant:

- My properties (L2) lists each unit with its dates and status, but not its rent.
- Property (L3) shows lease terms, deposit and schedule, but not the unit details (type, bedrooms, area, furnished). `get_lease` does not return them for a tenant.

The mode B grouping by landlord on My properties is in place.

## 5. Maintenance decision in mode B

Only the user linked to the property owner approves or rejects, and the code already works this way. A Property Manager decides on the company's own properties by being a Portal User of the company's Customer. Sections 3 and 5 of `doc/app-usage-flows-immo.md`, the mode B screens and the "Mode B" line of `CLAUDE.md` still say the property manager approves, so they need updating to match.

## 6. Minor points

- `download()` resets `ignore_print_permissions` to `False` instead of restoring the previous value, as IMMO-03 does. Location: `sky_immo/api.py:386`.
- The branch does not start from `develop`. It carries commits `addd8a2` and `10ba252` from `sky-immo-demo-branch`. Rebasing on `develop` after point 1 will make the diff easier to review.
