"""What each Sky-immo user may see: the one place that computes it.

Landlord and Tenant hold no DocPerm on PropMS or ERPNext doctypes, so the app never relies on
Frappe's permission engine for them. Every endpoint calls `get_scope` first and serves only what
it returns; `ignore_permissions` and `frappe.get_all` are used only on data already scoped here.
"""

from dataclasses import dataclass

import frappe

MANAGER_ROLES = frozenset({"System Manager", "Property Manager"})
LANDLORD = "Landlord"
TENANT = "Tenant"


@dataclass(frozen=True)
class Scope:
	user: str
	is_manager: bool
	# Customers the user is a portal user of.
	customers: frozenset[str]
	# Properties whose effective owner is one of `customers`, or every property for a manager.
	owned_properties: frozenset[str]
	# Properties on the user's own leases, as a tenant.
	rented_properties: frozenset[str]
	leases: frozenset[str]

	@property
	def properties(self) -> frozenset[str]:
		return self.owned_properties | self.rented_properties


def get_scope(user: str | None = None) -> Scope:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	is_manager = bool(roles & MANAGER_ROLES)
	customers = frozenset() if is_manager else get_customers(user)

	if is_manager:
		owned = frozenset(frappe.get_all("Property", pluck="name"))
	elif LANDLORD in roles and customers:
		owned = get_owned_properties(customers)
	else:
		owned = frozenset()

	leases = set()
	if owned:
		leases.update(get_leases({"property": ["in", list(owned)]}))

	rented = frozenset()
	if TENANT in roles and customers and not is_manager:
		tenant_leases = get_leases({"lease_customer": ["in", list(customers)]})
		leases.update(tenant_leases)
		rented = frozenset(tenant_leases.values())

	return Scope(
		user=user,
		is_manager=is_manager,
		customers=customers,
		owned_properties=owned,
		rented_properties=rented,
		leases=frozenset(leases),
	)


def get_customers(user: str) -> frozenset[str]:
	"""Customers that list the user in their Portal Users table."""
	return frozenset(
		frappe.get_all(
			"Portal User",
			filters={"parenttype": "Customer", "parentfield": "portal_users", "user": user},
			pluck="parent",
		)
	)


def get_owned_properties(customers: frozenset[str]) -> frozenset[str]:
	"""Properties whose owner is in `customers`; a property with no owner takes its nearest parent's."""
	properties = {
		p.name: p for p in frappe.get_all("Property", fields=["name", "parent_property", "unit_owner"])
	}

	def effective_owner(name: str | None) -> str | None:
		while name and name in properties:
			if properties[name].unit_owner:
				return properties[name].unit_owner
			name = properties[name].parent_property
		return None

	return frozenset(name for name in properties if effective_owner(name) in customers)


def get_leases(filters: dict) -> dict[str, str]:
	"""Lease name -> property, for leases matching `filters`. Draft leases are never shown."""
	rows = frappe.get_all(
		"Lease",
		filters={**filters, "lease_status": ["!=", "Draft"]},
		fields=["name", "property"],
	)
	return {row.name: row.property for row in rows}


def get_invoices(scope: Scope, fields: list[str] | None = None) -> list[dict]:
	"""Submitted invoices of the leases in scope, whoever the payer is."""
	if not scope.leases:
		return []
	return frappe.get_all(
		"Sales Invoice",
		filters={"lease": ["in", list(scope.leases)], "docstatus": 1},
		fields=fields or ["name"],
	)


def get_issues(scope: Scope, fields: list[str] | None = None) -> list[dict]:
	"""Maintenance requests: all of an owned property's, and a tenant's own on their rented units."""
	issue = frappe.qb.DocType("Issue")
	conditions = []
	if scope.owned_properties:
		conditions.append(issue.property_name.isin(list(scope.owned_properties)))
	if scope.rented_properties:
		# A tenant must not read requests raised by a former or another tenant of the same unit.
		conditions.append(
			issue.property_name.isin(list(scope.rented_properties))
			& (issue.customer.isin(list(scope.customers)) | (issue.raised_by == scope.user))
		)
	if not conditions:
		return []

	where = conditions[0]
	for condition in conditions[1:]:
		where |= condition
	columns = [issue[f] for f in fields or ["name"]]
	return frappe.qb.from_(issue).select(*columns).where(where).run(as_dict=True)
