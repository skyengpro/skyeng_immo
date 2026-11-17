"""What each Sky-immo user may see: the one place that computes it.

Landlord and Tenant hold no DocPerm on PropMS or ERPNext doctypes, so the app never relies on
Frappe's permission engine for them. Every endpoint calls `get_scope` first and serves only what
it returns; `ignore_permissions` and `frappe.get_all` are used only on data already scoped here.
"""

from dataclasses import dataclass

import frappe
from frappe.query_builder import Order

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


def is_manager(user: str | None = None) -> bool:
	"""Property Manager or System Manager, who work in Desk and may see every property."""
	return not MANAGER_ROLES.isdisjoint(frappe.get_roles(user))


def get_scope(user: str | None = None) -> Scope:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	manager = is_manager(user)
	customers = frozenset() if manager else get_customers(user)

	if manager:
		owned = frozenset(frappe.get_all("Property", pluck="name"))
	elif LANDLORD in roles and customers:
		owned = get_owned_properties(customers)
	else:
		owned = frozenset()

	leases = set()
	if owned:
		leases.update(find_leases({"property": ["in", list(owned)]}))

	rented = frozenset()
	if TENANT in roles and customers and not manager:
		tenant_leases = find_leases({"lease_customer": ["in", list(customers)]})
		leases.update(tenant_leases)
		rented = frozenset(tenant_leases.values())

	return Scope(
		user=user,
		is_manager=manager,
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


def find_leases(filters: dict) -> dict[str, str]:
	"""Lease name -> property, for leases matching `filters`. Draft leases are never shown."""
	rows = frappe.get_all(
		"Lease",
		filters={**filters, "lease_status": ["!=", "Draft"]},
		fields=["name", "property"],
	)
	return {row.name: row.property for row in rows}


def get_named(doctype: str, names: frozenset[str], fields: list[str] | None, order_by: str) -> list[dict]:
	"""Rows of `doctype` for names already in scope."""
	if not names:
		return []
	return frappe.get_all(
		doctype, filters={"name": ["in", list(names)]}, fields=fields or ["name"], order_by=order_by
	)


def get_properties(scope: Scope, fields: list[str] | None = None) -> list[dict]:
	return get_named("Property", scope.properties, fields, "lft")


def get_leases(scope: Scope, fields: list[str] | None = None) -> list[dict]:
	return get_named("Lease", scope.leases, fields, "start_date desc")


def invoice_filters(scope: Scope) -> dict:
	"""Submitted invoices of the leases in scope, whoever the payer is."""
	return {"lease": ["in", list(scope.leases)], "docstatus": 1}


def get_invoices(scope: Scope, fields: list[str] | None = None) -> list[dict]:
	if not scope.leases:
		return []
	return frappe.get_all(
		"Sales Invoice",
		filters=invoice_filters(scope),
		fields=fields or ["name"],
		order_by="posting_date desc, creation desc",
	)


def check_invoice(scope: Scope, name: str) -> None:
	"""Raise PermissionError (HTTP 403) unless the invoice is in scope; a missing one is refused alike."""
	if not scope.leases or not frappe.db.exists("Sales Invoice", {**invoice_filters(scope), "name": name}):
		raise frappe.PermissionError


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
	query = frappe.qb.from_(issue).select(*columns).where(where).orderby(issue.creation, order=Order.desc)
	return query.run(as_dict=True)
