import frappe
from frappe.tests import IntegrationTestCase

from skyeng_immo import api
from skyeng_immo.tests.utils import SharedSite

# Endpoint -> the key of SharedSite.expected() it must serve.
READ_ENDPOINTS = {
	api.get_properties: "properties",
	api.get_leases: "leases",
	api.get_invoices: "invoices",
	api.get_maintenance_requests: "issues",
}


class TestReadEndpoints(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def call(self, endpoint, user: str) -> list[dict]:
		with self.set_user(user):
			return endpoint()

	def test_each_user_receives_only_their_own_data(self):
		s = self.site
		for user, expected in s.expected().items():
			for endpoint, kind in READ_ENDPOINTS.items():
				with self.subTest(user=user, endpoint=endpoint.__name__):
					rows = self.call(endpoint, s.users[user])
					self.assertEqual({row.name for row in rows}, expected[kind])

	def test_property_manager_receives_leases_but_no_drafts(self):
		s = self.site
		leases = {r.name for r in self.call(api.get_leases, s.users["manager"])}
		self.assertTrue({s.lease_old, s.lease_1a, s.lease_2a} <= leases)
		self.assertNotIn(s.lease_draft, leases)

	def test_property_rows_are_in_tree_order_and_hide_the_owner(self):
		s = self.site
		rows = self.call(api.get_properties, s.users["landlord1"])
		self.assertEqual([r.name for r in rows], [s.building1, s.unit1a])
		self.assertNotIn("unit_owner", rows[0])

	def test_endpoints_are_get_only_and_closed_to_guests(self):
		for endpoint in (*READ_ENDPOINTS, api.download_invoice_pdf):
			with self.subTest(endpoint=endpoint.__name__):
				self.assertIn(endpoint, frappe.whitelisted)
				self.assertNotIn(endpoint, frappe.guest_methods)
				self.assertEqual(frappe.allowed_http_methods_for_whitelisted_func[endpoint], ["GET"])
				with self.set_user("Guest"), self.assertRaises(frappe.PermissionError):
					frappe.is_whitelisted(endpoint)
