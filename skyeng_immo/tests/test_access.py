import frappe
from frappe.api.v1 import read_doc
from frappe.client import get_list
from frappe.tests import IntegrationTestCase

from skyeng_immo.access import get_invoices, get_issues, get_scope
from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.tests.utils import SharedSite


def names(rows: list[dict]) -> set[str]:
	return {row.name for row in rows}


class TestScope(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def test_each_user_gets_exactly_their_own_data(self):
		s = self.site
		expected = {
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
		for user, data in expected.items():
			scope = get_scope(s.users[user])
			actual = {
				"properties": set(scope.properties),
				"leases": set(scope.leases),
				"invoices": names(get_invoices(scope)),
				"issues": names(get_issues(scope)),
			}
			for kind in data:
				with self.subTest(user=user, kind=kind):
					self.assertEqual(actual[kind], data[kind])

	def test_property_manager_gets_every_property(self):
		scope = get_scope(self.site.users["manager"])
		self.assertEqual(set(scope.properties), set(frappe.get_all("Property", pluck="name")))
		self.assertIn(self.site.invoice_1a, names(get_invoices(scope)))
		self.assertNotIn(self.site.invoice_unsubmitted, names(get_invoices(scope)))

	def test_role_without_customer_link_gets_nothing(self):
		scope = get_scope(make_user("_test_immo_scope_unlinked@example.com", ["Landlord", "Tenant"]))
		self.assertFalse(scope.properties or scope.leases)
		self.assertEqual(get_invoices(scope), [])
		self.assertEqual(get_issues(scope), [])

	def test_customer_link_without_role_gets_nothing(self):
		user = self.site.users["landlord1"]
		make_user(user, [])
		try:
			self.assertFalse(get_scope(user).properties)
		finally:
			make_user(user, ["Landlord"])


class TestRestApiIsClosed(IntegrationTestCase):
	"""Landlord and Tenant hold no DocPerm: /api/resource answers 403 even on their own records."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def test_resource_api_refuses_landlords_and_tenants(self):
		s = self.site
		own_records = {
			"landlord1": {
				"Property": s.unit1a,
				"Lease": s.lease_1a,
				"Sales Invoice": s.invoice_1a,
				"Issue": s.issue_1a,
				"Customer": s.customers["Landlord 1"],
			},
			"tenant1": {
				"Property": s.unit1a,
				"Lease": s.lease_1a,
				"Sales Invoice": s.invoice_1a,
				"Issue": s.issue_1a,
				"Customer": s.customers["Tenant 1"],
			},
		}
		for user, records in own_records.items():
			for doctype, name in records.items():
				with self.subTest(user=user, doctype=doctype), self.set_user(s.users[user]):
					with self.assertRaises(frappe.PermissionError):
						get_list(doctype)
					with self.assertRaises(frappe.PermissionError):
						read_doc(doctype, name)
