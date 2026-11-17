from unittest.mock import patch

import frappe
from frappe.auth import CookieManager, LoginManager
from frappe.tests import IntegrationTestCase
from frappe.utils import set_request
from frappe.utils.password import update_password
from frappe.website.utils import get_home_page

from skyeng_immo.immobilier.doctype.sky_immo_settings.sky_immo_settings import (
	MODE_CUSTOMER,
	MODE_SKY,
	get_operating_mode,
)
from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.navigation import has_app_permission
from skyeng_immo.www import sky_immo

PASSWORD = "Immo-Test-Pass-7391!"


def make_signing_user(email: str, roles: list[str]) -> str:
	make_user(email, roles)
	update_password(email, PASSWORD)
	return email


def sign_in(email: str) -> dict:
	"""Run Frappe's own sign-in and return the response the login page receives."""
	set_request(method="POST", path="/api/method/login")
	frappe.form_dict.update(usr=email, pwd=PASSWORD)
	frappe.local.response = frappe._dict()
	frappe.local.request_ip = "127.0.0.1"
	frappe.local.cookie_manager = CookieManager()
	try:
		frappe.local.login_manager = LoginManager()
		return dict(frappe.local.response)
	finally:
		frappe.form_dict.clear()
		frappe.set_user("Administrator")


class SignInTestCase(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		self.addCleanup(self.set_mode, get_operating_mode())
		# Frappe skips its landing-page cache on a dev server, which is what these tests exercise.
		patcher = patch.object(frappe, "_dev_server", False)
		patcher.start()
		self.addCleanup(patcher.stop)

	def set_mode(self, mode: str) -> None:
		settings = frappe.get_single("Sky Immo Settings")
		settings.operating_mode = mode
		settings.save(ignore_permissions=True)


class TestLanding(SignInTestCase):
	def test_landlord_and_tenant_land_on_the_app_in_both_modes(self):
		users = {
			role: make_signing_user(f"_test_immo_signin_{role.lower()}@example.com", [role])
			for role in ("Landlord", "Tenant")
		}
		for mode in (MODE_SKY, MODE_CUSTOMER):
			self.set_mode(mode)
			for role, email in users.items():
				with self.subTest(role=role, mode=mode):
					self.assertEqual(sign_in(email)["home_page"], "/sky-immo")

	def test_manager_lands_on_the_app_only_when_a_customer_owns_the_site(self):
		for role in ("Property Manager", "System Manager"):
			email = make_signing_user(
				f"_test_immo_signin_{role.lower().replace(' ', '_')}@example.com", [role]
			)
			self.set_mode(MODE_SKY)
			with self.subTest(role=role, mode=MODE_SKY):
				self.assertEqual(sign_in(email)["home_page"].strip("/"), "desk")

			self.set_mode(MODE_CUSTOMER)
			with self.subTest(role=role, mode=MODE_CUSTOMER):
				self.assertEqual(sign_in(email)["home_page"].strip("/"), "sky-immo")

	def test_changing_the_mode_refreshes_the_landing_page_of_a_signed_in_manager(self):
		# Sign-in clears the user's cache itself; a manager already signed in relies on the settings.
		email = make_user("_test_immo_signin_cached_pm@example.com", ["Property Manager"])
		self.set_mode(MODE_SKY)
		with self.set_user(email):
			frappe.session.data.user_type = "System User"
			frappe.cache.hdel("home_page", email)
			self.assertEqual(get_home_page(), "desk")

			self.set_mode(MODE_CUSTOMER)
			self.assertEqual(get_home_page(), "sky-immo")

	def test_staff_without_manager_role_is_not_redirected(self):
		email = make_signing_user("_test_immo_signin_sales@example.com", ["Sales User"])
		self.set_mode(MODE_CUSTOMER)
		self.assertEqual(sign_in(email)["home_page"].strip("/"), "desk")


class TestAppPage(SignInTestCase):
	def open_page(self, email: str):
		set_request(method="GET", path="/sky-immo")
		with self.set_user(email):
			return sky_immo.get_context(frappe._dict())

	def test_sky_owned_site_sends_managers_to_desk(self):
		self.set_mode(MODE_SKY)
		for role in ("Property Manager", "System Manager"):
			email = make_signing_user(f"_test_immo_page_{role.lower().replace(' ', '_')}@example.com", [role])
			with self.subTest(role=role), self.assertRaises(frappe.Redirect) as raised:
				self.open_page(email)
			self.assertEqual(raised.exception.http_status_code, 302)
			self.assertEqual(frappe.flags.redirect_location, "/desk")

	def test_page_opens_for_managers_of_a_customer_site_and_for_landlords_and_tenants(self):
		cases = {
			(MODE_CUSTOMER, "Property Manager"): "_test_immo_page_pm_b@example.com",
			(MODE_SKY, "Landlord"): "_test_immo_page_landlord_a@example.com",
			(MODE_CUSTOMER, "Tenant"): "_test_immo_page_tenant_b@example.com",
		}
		for (mode, role), email in cases.items():
			make_signing_user(email, [role])
			self.set_mode(mode)
			with self.subTest(mode=mode, role=role):
				self.assertEqual(self.open_page(email).boot["session_user"], email)

	def test_a_manager_who_is_also_a_landlord_is_treated_as_a_manager(self):
		self.set_mode(MODE_SKY)
		email = make_signing_user("_test_immo_page_both@example.com", ["Property Manager", "Landlord"])
		with self.assertRaises(frappe.Redirect):
			self.open_page(email)


class TestAppsScreen(SignInTestCase):
	def test_tile_is_offered_to_those_who_can_use_the_app(self):
		users = {
			"landlord": make_user("_test_immo_tile_landlord@example.com", ["Landlord"]),
			"tenant": make_user("_test_immo_tile_tenant@example.com", ["Tenant"]),
			"manager": make_user("_test_immo_tile_manager@example.com", ["Property Manager"]),
			"other staff": make_user("_test_immo_tile_sales@example.com", ["Sales User"]),
			"Guest": "Guest",
		}
		expected = {
			MODE_SKY: {
				"landlord": True,
				"tenant": True,
				"manager": False,
				"other staff": False,
				"Guest": False,
			},
			MODE_CUSTOMER: {
				"landlord": True,
				"tenant": True,
				"manager": True,
				"other staff": False,
				"Guest": False,
			},
		}
		for mode, per_user in expected.items():
			self.set_mode(mode)
			for label, want in per_user.items():
				with self.subTest(mode=mode, user=label), self.set_user(users[label]):
					self.assertIs(has_app_permission(), want)


class TestDefaultApp(SignInTestCase):
	def test_website_user_with_an_app_role_gets_the_app_as_default(self):
		for role in ("Landlord", "Tenant"):
			email = make_user(f"_test_immo_default_{role.lower()}@example.com", [role])
			with self.subTest(role=role):
				self.assertEqual(frappe.db.get_value("User", email, "default_app"), "skyeng_immo")

	def test_chosen_default_app_and_staff_are_left_alone(self):
		chosen = make_user("_test_immo_default_chosen@example.com", [])
		frappe.db.set_value("User", chosen, "default_app", "erpnext")
		frappe.get_doc("User", chosen).add_roles("Landlord")
		self.assertEqual(frappe.db.get_value("User", chosen, "default_app"), "erpnext")

		staff = make_user("_test_immo_default_staff@example.com", ["Property Manager", "Landlord"])
		self.assertEqual(frappe.db.get_value("User", staff, "user_type"), "System User")
		self.assertFalse(frappe.db.get_value("User", staff, "default_app"))

		plain = make_user("_test_immo_default_plain@example.com", ["Sales User"])
		self.assertFalse(frappe.db.get_value("User", plain, "default_app"))
