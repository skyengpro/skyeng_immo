import frappe
from frappe.tests import IntegrationTestCase

from skyeng_immo.immobilier.doctype.sky_immo_settings.sky_immo_settings import (
	MODE_CUSTOMER,
	MODE_SKY,
	get_operating_mode,
)

TEST_USERS = {
	"System Manager": "_test_immo_sysman@example.com",
	"Property Manager": "_test_immo_pm@example.com",
	"Landlord": "_test_immo_landlord@example.com",
	"Tenant": "_test_immo_tenant@example.com",
}


def make_user(email: str, roles: list[str]) -> str:
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": "_Test", "send_welcome_email": 0}
		).insert(ignore_permissions=True)
	user = frappe.get_doc("User", email)
	user.set("roles", [])
	user.add_roles(*roles)
	return email


class TestSkyImmoSettings(IntegrationTestCase):
	def test_operating_mode_offers_exactly_the_two_modes(self):
		field = frappe.get_meta("Sky Immo Settings").get_field("operating_mode")
		self.assertEqual(field.fieldtype, "Select")
		self.assertEqual(field.options.split("\n"), [MODE_SKY, MODE_CUSTOMER])

	def test_operating_mode_round_trips(self):
		settings = frappe.get_single("Sky Immo Settings")
		settings.operating_mode = MODE_CUSTOMER
		settings.save(ignore_permissions=True)
		self.assertEqual(get_operating_mode(), MODE_CUSTOMER)

	def test_only_system_and_property_managers_can_open_and_edit(self):
		for role, email in TEST_USERS.items():
			make_user(email, [role])
			allowed = role in ("System Manager", "Property Manager")
			for ptype in ("read", "write"):
				with self.subTest(role=role, ptype=ptype):
					self.assertEqual(
						bool(frappe.has_permission("Sky Immo Settings", ptype, user=email)), allowed
					)
