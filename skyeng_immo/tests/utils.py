"""Factories for a site shared by two landlords and two tenants. All data is obviously fake."""

import frappe
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
from frappe.utils import add_months, nowdate
from propms.tests.utils import create_customer, create_item, create_property

from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.invitation import link_portal_user

# Bootstrapped by erpnext.tests.utils, imported through test_sales_invoice above.
COMPANY = "_Test Company"
CURRENCY = "INR"


def make_property(name: str, owner: str | None = None, parent: str | None = None, is_group: int = 0) -> str:
	return create_property(name, company=COMPANY, unit_owner=owner, parent_property=parent, is_group=is_group)


def make_lease(property_name: str, tenant: str, past: bool = False, **kwargs) -> str:
	"""One-line monthly lease. With `past`, it ended a year ago, so PropMS sets it Expired.

	The tenant is the lease's single Customer (EP-01, checked by `validate_lease`).
	"""
	start = add_months(nowdate(), -24 if past else 0)
	doc = frappe.get_doc(
		{
			"doctype": "Lease",
			"property": property_name,
			"lease_date": start,
			"lease_customer": tenant,
			"customer": tenant,
			"start_date": start,
			"end_date": add_months(start, 12),
			"notice_period": 30,
			"security_deposit_currency": CURRENCY,
			"lease_item": [
				{
					"lease_item": create_item("_Test Immo Rent"),
					"frequency": "Monthly",
					"amount": 100,
					"currency_code": CURRENCY,
					"paid_by": tenant,
					"document_type": "Sales Invoice",
				}
			],
			**kwargs,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def make_invoice(lease: str, customer: str, submit: bool = True) -> str:
	invoice = create_sales_invoice(customer=customer, rate=100, do_not_save=True)
	invoice.lease = lease
	invoice.insert(ignore_permissions=True)
	if submit:
		invoice.submit()
	return invoice.name


def make_issue(property_name: str, customer: str, raised_by: str) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Issue",
			"subject": "_Test Immo leak",
			"property_name": property_name,
			"customer": customer,
			"raised_by": raised_by,
		}
	)
	# PropMS makes staff fields (person_in_charge, issue_type) mandatory; scope does not read them.
	doc.flags.ignore_mandatory = True
	return doc.insert(ignore_permissions=True).name


class SharedSite:
	"""Two landlords, two tenants and a property manager, with data placed to catch each leak.

	Building 1 (landlord 1): unit 1A inherits landlord 1, unit 1B has its own owner, landlord 2.
	Building 2 (landlord 2): floor 2 and unit 2A inherit landlord 2 through two levels.
	"""

	def __init__(self):
		self.customers = {
			key: create_customer(f"_Test Immo {key}")
			for key in ("Landlord 1", "Landlord 2", "Tenant 1", "Tenant 2", "Payer")
		}
		c = self.customers

		self.users = {
			"landlord1": make_user("_test_immo_scope_landlord1@example.com", ["Landlord"]),
			"landlord2": make_user("_test_immo_scope_landlord2@example.com", ["Landlord"]),
			"tenant1": make_user("_test_immo_scope_tenant1@example.com", ["Tenant"]),
			"tenant2": make_user("_test_immo_scope_tenant2@example.com", ["Tenant"]),
			"manager": make_user("_test_immo_scope_manager@example.com", ["Property Manager"]),
		}
		u = self.users
		for user, customer in (
			("landlord1", "Landlord 1"),
			("landlord2", "Landlord 2"),
			("tenant1", "Tenant 1"),
			("tenant2", "Tenant 2"),
		):
			link_portal_user(c[customer], u[user])

		self.building1 = make_property("_Test Immo Building 1", owner=c["Landlord 1"], is_group=1)
		self.unit1a = make_property("_Test Immo Unit 1A", parent=self.building1)
		self.unit1b = make_property("_Test Immo Unit 1B", owner=c["Landlord 2"], parent=self.building1)
		self.building2 = make_property("_Test Immo Building 2", owner=c["Landlord 2"], is_group=1)
		self.floor2 = make_property("_Test Immo Floor 2", parent=self.building2, is_group=1)
		self.unit2a = make_property("_Test Immo Unit 2A", parent=self.floor2)

		# Tenant 2 used to rent 1A; tenant 1 rents it now. Its invoice is billed to a third party:
		# invoices are found through the lease, whoever the payer is.
		self.lease_old = make_lease(self.unit1a, c["Tenant 2"], past=True)
		self.lease_1a = make_lease(self.unit1a, c["Tenant 1"])
		self.lease_2a = make_lease(self.unit2a, c["Tenant 2"])
		self.lease_draft = make_lease(self.unit1b, c["Tenant 1"], lease_status="Draft")

		self.invoice_1a = make_invoice(self.lease_1a, c["Payer"])
		self.invoice_2a = make_invoice(self.lease_2a, c["Tenant 2"])
		self.invoice_old = make_invoice(self.lease_old, c["Tenant 2"])
		self.invoice_unsubmitted = make_invoice(self.lease_1a, c["Payer"], submit=False)

		self.issue_1a = make_issue(self.unit1a, c["Tenant 1"], u["tenant1"])
		self.issue_1a_old = make_issue(self.unit1a, c["Tenant 2"], u["tenant2"])
		self.issue_2a = make_issue(self.unit2a, c["Tenant 2"], u["tenant2"])
		self.issue_1b = make_issue(self.unit1b, c["Landlord 2"], u["landlord2"])

	def expected(self) -> dict[str, dict[str, set[str]]]:
		"""What each user may see, for the scope and the API tests to check against."""
		s = self
		return {
			"landlord1": {
				# 1A inherits landlord 1 from building 1; 1B has its own owner and is not theirs.
				"properties": {s.building1, s.unit1a},
				"leases": {s.lease_old, s.lease_1a},
				"invoices": {s.invoice_1a, s.invoice_old},
				"issues": {s.issue_1a, s.issue_1a_old},
			},
			"landlord2": {
				# 2A inherits landlord 2 through floor 2; 1B is theirs inside landlord 1's building.
				"properties": {s.unit1b, s.building2, s.floor2, s.unit2a},
				"leases": {s.lease_2a},
				"invoices": {s.invoice_2a},
				"issues": {s.issue_2a, s.issue_1b},
			},
			"tenant1": {
				# The draft lease on 1B is hidden; 1A's invoice is theirs although a third party pays it.
				"properties": {s.unit1a},
				"leases": {s.lease_1a},
				"invoices": {s.invoice_1a},
				# The request tenant 2 raised on 1A before moving out is not theirs.
				"issues": {s.issue_1a},
			},
			"tenant2": {
				"properties": {s.unit1a, s.unit2a},
				"leases": {s.lease_old, s.lease_2a},
				"invoices": {s.invoice_old, s.invoice_2a},
				"issues": {s.issue_1a_old, s.issue_2a},
			},
		}
