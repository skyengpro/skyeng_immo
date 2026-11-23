import frappe
from frappe.api.v1 import read_doc
from frappe.client import get_list
from frappe.tests import IntegrationTestCase

from skyeng_immo.access import get_invoices, get_issues, get_scope
from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.tests.utils import SharedSite


class TestScope(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def test_property_manager_gets_every_property(self):
		scope = get_scope(self.site.users["manager"])
		self.assertEqual(set(scope.properties), set(frappe.get_all("Property", pluck="name")))
		invoices = {row.name for row in get_invoices(scope, ["name"])}
		self.assertIn(self.site.invoice_1a, invoices)
		self.assertNotIn(self.site.invoice_unsubmitted, invoices)

	def test_role_without_customer_link_gets_nothing(self):
		scope = get_scope(make_user("_test_immo_scope_unlinked@example.com", ["Landlord", "Tenant"]))
		self.assertFalse(scope.properties or scope.leases)
		self.assertEqual(get_invoices(scope, ["name"]), [])
		self.assertEqual(get_issues(scope, ["name"]), [])

	def test_customer_link_without_role_gets_nothing(self):
		user = self.site.users["landlord1"]
		make_user(user, [])
		try:
			self.assertFalse(get_scope(user).properties)
		finally:
			make_user(user, ["Landlord"])

	def test_disabled_customer_gives_no_access(self):
		s = self.site
		customer = s.customers["Landlord 1"]
		frappe.db.set_value("Customer", customer, "disabled", 1)
		try:
			scope = get_scope(s.users["landlord1"])
			self.assertFalse(scope.customers or scope.properties or scope.leases)
		finally:
			frappe.db.set_value("Customer", customer, "disabled", 0)

	def test_a_cycle_in_the_property_tree_does_not_hang(self):
		s = self.site
		# NestedSet refuses cycles on save; direct writes, as an import could do, create one.
		# Neither unit has its own owner, so the search for an owner has to stop on its own.
		frappe.db.set_value("Property", s.unit1a, "parent_property", s.floor2)
		frappe.db.set_value("Property", s.floor2, "parent_property", s.unit1a)
		try:
			get_scope(s.users["landlord1"])
		finally:
			frappe.db.set_value("Property", s.unit1a, "parent_property", s.building1)
			frappe.db.set_value("Property", s.floor2, "parent_property", s.building2)


class TestRestApiIsClosed(IntegrationTestCase):
	"""Landlord and Tenant hold no DocPerm: /api/resource answers 403 even on their own records."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def test_resource_api_refuses_landlords_and_tenants(self):
		s = self.site
		records = {
			"Property": s.unit1a,
			"Lease": s.lease_1a,
			"Sales Invoice": s.invoice_1a,
			"Issue": s.issue_1a,
		}
		own_customer = {"landlord1": s.customers["Landlord 1"], "tenant1": s.customers["Tenant 1"]}
		for user, customer in own_customer.items():
			for doctype, name in {**records, "Customer": customer}.items():
				with self.subTest(user=user, doctype=doctype), self.set_user(s.users[user]):
					with self.assertRaises(frappe.PermissionError):
						get_list(doctype)
					with self.assertRaises(frappe.PermissionError):
						read_doc(doctype, name)
