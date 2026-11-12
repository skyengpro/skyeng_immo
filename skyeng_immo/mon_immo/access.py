"""Who sees what in Mon Immo.

Every app endpoint starts from :func:`get_scope`, and every list it returns is
filtered by the scope. This is the only separation between landlords who
share one site (EP-01, mode A), so the rules are kept here, in one place:

=====================================  ===============================================
Role                                   Properties visible
=====================================  ===============================================
System Manager / Property Manager      every property on the site
Landlord                               ``unit_owner`` is one of their Customers, plus
                                       every unit below such a property in the tree
Tenant                                 the properties on their leases
=====================================  ===============================================

An account is tied to its Customer(s) the ERPNext way: a row in the
Customer's *Portal Users* table (or, as a fallback, a Contact whose ``user``
is the account and which links to the Customer).
"""

from dataclasses import dataclass, field

import frappe

MANAGER_ROLES = ("System Manager", "Property Manager")
LANDLORD_ROLE = "Landlord"
TENANT_ROLE = "Tenant"

# Leases that never existed for the people concerned.
HIDDEN_LEASE_STATUSES = ("Draft", "Not Materialized")


def app_role(user: str | None = None) -> str | None:
	"""The app space of a user: ``manager``, ``owner``, ``tenant``, or ``None``.

	Staff win over landlords, who win over tenants: a property manager who is
	also a tenant somewhere still gets the management screens.
	"""
	user = user or frappe.session.user
	if user == "Guest":
		return None
	roles = set(frappe.get_roles(user))
	if roles.intersection(MANAGER_ROLES):
		return "manager"
	if LANDLORD_ROLE in roles:
		return "owner"
	if TENANT_ROLE in roles:
		return "tenant"
	return None


def linked_customers(user: str) -> list[str]:
	"""Customers the account acts for, through Portal Users or a linked Contact."""
	customers = set(
		frappe.get_all(
			"Portal User",
			filters={"user": user, "parenttype": "Customer"},
			pluck="parent",
			ignore_permissions=True,
		)
	)
	contacts = frappe.get_all("Contact", filters={"user": user}, pluck="name", ignore_permissions=True)
	if contacts:
		customers.update(
			frappe.get_all(
				"Dynamic Link",
				filters={"parenttype": "Contact", "parent": ["in", contacts], "link_doctype": "Customer"},
				pluck="link_name",
				ignore_permissions=True,
			)
		)
	return sorted(customers)


@dataclass
class Scope:
	user: str
	role: str
	customers: list[str] = field(default_factory=list)
	_properties: set[str] | None = None
	_leases: list[str] | None = None

	@property
	def is_manager(self) -> bool:
		return self.role == "manager"

	def properties(self) -> set[str]:
		"""Names of every Property this user may see."""
		if self._properties is None:
			self._properties = self._compute_properties()
		return self._properties

	def _compute_properties(self) -> set[str]:
		if self.is_manager:
			return set(frappe.get_all("Property", pluck="name", ignore_permissions=True))
		if not self.customers:
			return set()
		if self.role == "owner":
			owned = frappe.get_all(
				"Property",
				filters={"unit_owner": ["in", self.customers]},
				fields=["name", "lft", "rgt"],
				ignore_permissions=True,
			)
			names = {row.name for row in owned}
			# Access to a building covers its units, whoever they are recorded under.
			for row in owned:
				if row.lft and row.rgt and row.rgt - row.lft > 1:
					names.update(
						frappe.get_all(
							"Property",
							filters={"lft": [">", row.lft], "rgt": ["<", row.rgt]},
							pluck="name",
							ignore_permissions=True,
						)
					)
			return names
		# Tenant: the properties on their leases.
		return {
			row.property
			for row in frappe.get_all(
				"Lease",
				filters=self._lease_filters(),
				fields=["property"],
				ignore_permissions=True,
			)
			if row.property
		}

	def _lease_filters(self) -> dict:
		filters: dict = {"lease_status": ["not in", HIDDEN_LEASE_STATUSES], "docstatus": ["<", 2]}
		if self.role == "tenant":
			filters["customer"] = ["in", self.customers or [""]]
		elif not self.is_manager:
			filters["property"] = ["in", list(self.properties()) or [""]]
		return filters

	def leases(self) -> list[str]:
		"""Names of every Lease this user may see."""
		if self._leases is None:
			if self.role != "tenant" and not self.is_manager and not self.properties():
				self._leases = []
			else:
				self._leases = frappe.get_all(
					"Lease", filters=self._lease_filters(), pluck="name", ignore_permissions=True
				)
		return self._leases

	def invoice_filters(self) -> dict:
		"""Filters selecting the rent invoices this user may see."""
		filters: dict = {"docstatus": 1, "is_return": 0, "lease": ["in", self.leases() or [""]]}
		if self.role == "tenant":
			# The tenant sees what is billed to them, not another payer on the same lease.
			filters["customer"] = ["in", self.customers or [""]]
		return filters

	def can_see_property(self, name: str) -> bool:
		return bool(name) and name in self.properties()

	def can_see_lease(self, name: str) -> bool:
		return bool(name) and name in self.leases()

	def can_see_invoice(self, name: str) -> bool:
		if not name:
			return False
		return bool(
			frappe.get_all("Sales Invoice", filters={**self.invoice_filters(), "name": name}, limit=1)
		)


def get_scope(require: tuple[str, ...] | None = None) -> Scope:
	"""Scope of the signed-in user. Raises PermissionError when they have no app role.

	:param require: app roles allowed for this endpoint, for example ``("tenant",)``.
	"""
	user = frappe.session.user
	role = app_role(user)
	if role is None or (require and role not in require):
		frappe.throw(frappe._("You do not have access to this page."), frappe.PermissionError)
	customers = [] if role == "manager" else linked_customers(user)
	return Scope(user=user, role=role, customers=customers)


APP_NAME = "skyeng_immo"


def has_app_permission() -> bool:
	"""Mon Immo tile on Frappe's apps screen: shown to landlord and tenant accounts.

	Staff are left out on purpose: listing a non-desk app for them would change
	where Frappe sends them after sign-in (/apps instead of /desk). They open
	/mon-immo directly.
	"""
	user = frappe.session.user
	if user == "Guest" or frappe.get_cached_value("User", user, "user_type") != "Website User":
		return False
	return app_role(user) in ("owner", "tenant")


def set_default_app(doc, method=None):
	"""User.validate: landlord and tenant accounts open Mon Immo after sign-in and after setting a password.

	Without it, Frappe's login sends website users to the first app on the apps
	screen, which can be a desk app they cannot use (PropMS).
	"""
	roles = {row.role for row in doc.get("roles") or []}
	if doc.user_type == "Website User" and roles & {LANDLORD_ROLE, TENANT_ROLE} and not doc.default_app:
		doc.default_app = APP_NAME


def not_found():
	"""Same answer for 'does not exist' and 'not yours', so names cannot be probed."""
	frappe.throw(frappe._("Not found"), frappe.DoesNotExistError)
