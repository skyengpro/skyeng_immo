"""The app's screens (skyeng_immo.sky_immo.api) on a site shared by two landlords and two tenants.

Same fixture and same expectations as the IMMO-03 read endpoints (`SharedSite.expected`): the
screens must serve exactly what `skyeng_immo.access.get_scope` allows, nothing more.
"""

import frappe
from frappe.tests import IntegrationTestCase

from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.invitation import link_portal_user
from skyeng_immo.sky_immo import api
from skyeng_immo.tests.utils import SharedSite, make_issue

LANDLORDS = ("landlord1", "landlord2")
TENANTS = ("tenant1", "tenant2")


def unit_ids(listing: dict) -> set[str]:
	return {
		unit["id"]
		for section in listing["sections"]
		for group in section["groups"]
		for unit in group["units"]
	}


def invoice_ids() -> set[str]:
	return {row["id"] for tab in ("unpaid", "paid") for row in api.list_invoices(tab)}


class TestAppEndpoints(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()
		cls.expected = cls.site.expected()
		s = cls.site
		cls.all_units = {s.unit1a, s.unit1b, s.unit2a}
		cls.all_leases = {s.lease_old, s.lease_1a, s.lease_2a}
		cls.all_issues = {s.issue_1a, s.issue_1a_old, s.issue_2a, s.issue_1b}

	def assert_refused(self, endpoint, *args):
		with self.assertRaises((frappe.DoesNotExistError, frappe.PermissionError)):
			endpoint(*args)

	def test_landlords_see_only_their_properties(self):
		for key in LANDLORDS:
			expected = self.expected[key]
			own_units = self.all_units & expected["properties"]
			with self.subTest(user=key), self.set_user(self.site.users[key]):
				self.assertEqual(unit_ids(api.list_properties()), own_units)
				for unit in self.all_units:
					if unit in own_units:
						self.assertEqual(api.get_property(unit)["id"], unit)
					else:
						self.assert_refused(api.get_property, unit)

	def test_unit_with_its_own_owner_is_not_the_building_owners(self):
		# Unit 1B sits in landlord 1's building but is owned by landlord 2.
		with self.set_user(self.site.users["landlord1"]):
			self.assert_refused(api.get_property, self.site.unit1b)
			self.assert_refused(api.get_issue, self.site.issue_1b)
		with self.set_user(self.site.users["landlord2"]):
			self.assertEqual(api.get_property(self.site.unit1b)["id"], self.site.unit1b)

	def test_each_user_gets_only_their_leases_invoices_and_requests(self):
		for key in (*LANDLORDS, *TENANTS):
			expected = self.expected[key]
			with self.subTest(user=key), self.set_user(self.site.users[key]):
				self.assertEqual(invoice_ids(), expected["invoices"])
				self.assertEqual({row["id"] for row in api.list_issues()}, expected["issues"])
				for lease in self.all_leases:
					if lease in expected["leases"]:
						self.assertEqual(api.get_lease(lease)["id"], lease)
					else:
						self.assert_refused(api.get_lease, lease)
				for issue in self.all_issues - expected["issues"]:
					self.assert_refused(api.get_issue, issue)
					self.assert_refused(api.issue_photo, issue)

	def test_tenant_sees_the_invoices_of_their_lease_whoever_pays(self):
		with self.set_user(self.site.users["tenant1"]):
			self.assertEqual({row["id"] for row in api.list_my_leases()}, {self.site.lease_1a})
			self.assertIn(self.site.invoice_1a, invoice_ids())

	def test_tenant_does_not_see_requests_on_a_unit_they_never_rented(self):
		s = self.site
		stray = make_issue(s.unit2a, s.customers["Tenant 1"], "_test_immo_someone@example.com")
		with self.set_user(s.users["tenant1"]):
			self.assertNotIn(stray, {row["id"] for row in api.list_issues()})
			self.assert_refused(api.get_issue, stray)

	def test_contact_without_portal_user_gets_nothing(self):
		user = make_user("_test_immo_contact_only@example.com", ["Landlord"])
		frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": "_Test Immo Contact Only",
				"user": user,
				"links": [{"link_doctype": "Customer", "link_name": self.site.customers["Landlord 2"]}],
			}
		).insert(ignore_permissions=True)
		with self.set_user(user):
			self.assertEqual(unit_ids(api.list_properties()), set())
			self.assertEqual(api.list_issues(), [])

	def test_user_without_lease_gets_no_invoice(self):
		# Frappe reads `lease in []` as "no lease": an empty scope must not list lease-less invoices.
		from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice
		from propms.tests.utils import create_customer

		stray = create_sales_invoice(customer=create_customer("_Test Immo Unrelated Buyer"), rate=50).name
		user = make_user("_test_immo_no_lease@example.com", ["Landlord"])
		link_portal_user(create_customer("_Test Immo Landlord Without Property"), user)
		with self.set_user(user):
			self.assertEqual(invoice_ids(), set())
			self.assert_refused(api.get_invoice, stray)

	def test_disabled_customer_loses_access(self):
		customer = self.site.customers["Landlord 2"]
		frappe.db.set_value("Customer", customer, "disabled", 1)
		try:
			with self.set_user(self.site.users["landlord2"]):
				self.assertEqual(unit_ids(api.list_properties()), set())
				self.assert_refused(api.get_property, self.site.unit2a)
		finally:
			frappe.db.set_value("Customer", customer, "disabled", 0)

	def test_landlord_who_is_also_a_tenant_gets_both_sides(self):
		s = self.site
		user = make_user("_test_immo_both_roles@example.com", ["Landlord", "Tenant"])
		link_portal_user(s.customers["Landlord 1"], user)
		link_portal_user(s.customers["Tenant 2"], user)
		with self.set_user(user):
			# Landlord screens: landlord 1's units only, not the unit rented as tenant 2.
			self.assertEqual(unit_ids(api.list_properties()), {s.unit1a})
			self.assert_refused(api.get_property, s.unit2a)
			self.assertEqual(
				{row["id"] for row in api.list_issues("owner")}, self.expected["landlord1"]["issues"]
			)
			self.assertEqual(
				{row["id"] for row in api.list_issues("tenant")}, self.expected["tenant2"]["issues"]
			)
			# Tenant screens: tenant 2's leases only.
			self.assertEqual({row["id"] for row in api.list_my_leases()}, self.expected["tenant2"]["leases"])
			self.assertEqual(
				invoice_ids(), self.expected["landlord1"]["invoices"] | self.expected["tenant2"]["invoices"]
			)

	def test_tenants_screen_lists_current_and_former_tenants_of_own_properties(self):
		s, c = self.site, self.site.customers
		with self.set_user(s.users["landlord1"]):
			rows = {row["id"]: row for row in api.list_tenants()["tenants"]}
		# Tenant 2 left unit 1A; their current home (2A, landlord 2) is not landlord 1's business.
		self.assertEqual(set(rows), {c["Tenant 1"], c["Tenant 2"]})
		self.assertTrue(rows[c["Tenant 1"]]["current"])
		self.assertEqual(rows[c["Tenant 1"]]["leaseId"], s.lease_1a)
		self.assertFalse(rows[c["Tenant 2"]]["current"])
		self.assertEqual(rows[c["Tenant 2"]]["leaseId"], s.lease_old)
		self.assertEqual([unit["id"] for unit in rows[c["Tenant 2"]]["units"]], [s.unit1a])

		with self.set_user(s.users["landlord2"]):
			listing = api.list_tenants()
		# The draft lease on 1B never ran: no tenant for it.
		self.assertEqual({row["id"] for row in listing["tenants"]}, {c["Tenant 2"]})
		self.assertFalse(listing["byLandlord"])

	def test_manager_sees_tenants_grouped_by_landlord(self):
		with self.set_user(self.site.users["manager"]):
			listing = api.list_tenants()
		self.assertTrue(listing["byLandlord"])
		mine = [row for row in listing["tenants"] if row["id"] in self.site.customers.values()]
		self.assertTrue(mine)
		self.assertTrue(all(row["landlord"] for row in mine))

	def test_manager_sees_their_own_customers_properties_and_tenants_apart(self):
		# Mode B: the customer's staff is a portal user of the customer's own Customer (here Landlord 1).
		s, c = self.site, self.site.customers
		manager = make_user("_test_immo_manager_own_customer@example.com", ["Property Manager"])
		link_portal_user(c["Landlord 1"], manager)
		with self.set_user(manager):
			sections = api.list_properties()["sections"]
			tenants = {row["id"]: row for row in api.list_tenants()["tenants"]}

		mine = {section["landlord"]["id"] for section in sections if section["mine"]}
		self.assertEqual(mine, {c["Landlord 1"]})
		self.assertIn(
			c["Landlord 2"], {s["landlord"]["id"] for s in sections if s["landlord"] and not s["mine"]}
		)
		self.assertTrue(tenants[c["Tenant 1"]]["mine"])  # current tenant of unit 1A, Landlord 1's
		self.assertFalse(tenants[c["Tenant 2"]]["mine"])  # current tenant of 2A, Landlord 2's

		# without a Customer of their own, nothing is the manager's
		with self.set_user(s.users["manager"]):
			self.assertFalse(any(section["mine"] for section in api.list_properties()["sections"]))
			self.assertFalse(any(row["mine"] for row in api.list_tenants()["tenants"]))

	def test_landlord_sees_everything_as_their_own(self):
		with self.set_user(self.site.users["landlord1"]):
			self.assertTrue(all(section["mine"] for section in api.list_properties()["sections"]))
			self.assertTrue(all(row["mine"] for row in api.list_tenants()["tenants"]))

	def test_lease_names_the_landlord_to_the_owner_side_only(self):
		s = self.site
		with self.set_user(s.users["landlord1"]):
			self.assertEqual(api.get_lease(s.lease_1a)["landlord"]["id"], s.customers["Landlord 1"])
		with self.set_user(s.users["tenant1"]):
			self.assertIsNone(api.get_lease(s.lease_1a)["landlord"])

	def test_property_screen_lists_its_requests_and_its_units(self):
		s = self.site
		with self.set_user(s.users["landlord1"]):
			unit = {row["id"] for row in api.get_property(s.unit1a)["issues"]}
			building = {row["id"] for row in api.get_property(s.building1)["issues"]}
		self.assertEqual(unit, {s.issue_1a, s.issue_1a_old})
		# Unit 1B sits in building 1 but is landlord 2's: its request stays out.
		self.assertEqual(building, {s.issue_1a, s.issue_1a_old})
		with self.set_user(s.users["landlord2"]):
			self.assertEqual({row["id"] for row in api.get_property(s.unit1b)["issues"]}, {s.issue_1b})

	def test_session_offers_the_spaces_of_the_roles_held(self):
		s = self.site
		both = make_user("_test_immo_both_spaces@example.com", ["Landlord", "Tenant"])
		cases = {
			s.users["landlord1"]: ["owner"],
			s.users["tenant1"]: ["tenant"],
			s.users["manager"]: ["owner"],
			both: ["owner", "tenant"],
		}
		for user, spaces in cases.items():
			with self.subTest(user=user), self.set_user(user):
				self.assertEqual(api.get_session()["user"]["spaces"], spaces)

	def test_tenant_lease_screen_shows_the_unit_and_the_rent(self):
		s = self.site
		with self.set_user(s.users["tenant2"]):
			lease = api.get_lease(s.lease_2a)
			listed = {row["id"]: row for row in api.list_my_leases()}
		self.assertEqual(lease["buildingName"], s.floor2)
		self.assertEqual(set(lease["features"]), {"type", "bedrooms", "bathrooms", "area", "furnished"})
		self.assertGreater(listed[s.lease_2a]["amountPerPeriod"], 0)
		self.assertEqual(listed[s.lease_2a]["frequency"], "monthly")

	def test_manager_sees_repairs_grouped_by_landlord(self):
		s = self.site
		with self.set_user(s.users["manager"]):
			rows = {row["id"]: row for row in api.list_issues("owner")}
		self.assertEqual(rows[s.issue_1a]["landlord"]["id"], s.customers["Landlord 1"])
		self.assertEqual(rows[s.issue_1b]["landlord"]["id"], s.customers["Landlord 2"])
		with self.set_user(s.users["landlord1"]):
			self.assertTrue(all(not row.get("landlord") for row in api.list_issues("owner")))

	def test_decisions_do_not_tell_a_stranger_whether_a_request_exists(self):
		from skyeng_immo.sky_immo import maintenance

		with self.set_user(self.site.users["landlord1"]):
			for name in (self.site.issue_2a, "ISS-DOES-NOT-EXIST"):
				with self.subTest(name=name), self.assertRaises(frappe.PermissionError):
					maintenance.decide(name, "approve")
		with self.set_user(self.site.users["tenant1"]):
			for name in (self.site.issue_2a, "ISS-DOES-NOT-EXIST"):
				with self.subTest(name=name), self.assertRaises(frappe.PermissionError):
					maintenance.complete(name)

	def test_screens_of_the_other_side_are_refused(self):
		with self.set_user(self.site.users["tenant1"]):
			for endpoint in (api.get_owner_dashboard, api.list_properties, api.list_tenants):
				self.assert_refused(endpoint)
		with self.set_user(self.site.users["landlord1"]):
			for endpoint in (api.get_tenant_home, api.list_my_leases):
				self.assert_refused(endpoint)
