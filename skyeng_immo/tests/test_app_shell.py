from unittest.mock import patch

import frappe
from frappe.gettext.translate import compile_translations
from frappe.modules.import_file import import_file_by_path
from frappe.tests import IntegrationTestCase
from frappe.translate import MERGED_TRANSLATION_KEY
from frappe.utils import set_request
from frappe.website.path_resolver import resolve_path

from skyeng_immo import install
from skyeng_immo.api import get_translations
from skyeng_immo.immobilier.doctype.sky_immo_settings.sky_immo_settings import MODE_CUSTOMER, MODE_SKY
from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.www import sky_immo

APP_ROLES = ("Landlord", "Tenant")


class TestRoles(IntegrationTestCase):
	def test_app_roles_exist_without_desk_access(self):
		for role in APP_ROLES:
			with self.subTest(role=role):
				self.assertEqual(frappe.db.get_value("Role", role, "desk_access"), 0)

	def test_fixture_restores_desk_access(self):
		frappe.db.set_value("Role", "Landlord", "desk_access", 1)
		import_file_by_path(
			frappe.get_app_path("skyeng_immo", "fixtures", "role.json"),
			data_import=True,
			force=True,
			reset_permissions=True,
		)
		self.assertEqual(frappe.db.get_value("Role", "Landlord", "desk_access"), 0)

	def test_app_role_only_user_is_refused_at_desk(self):
		from frappe.www import desk

		for role in APP_ROLES:
			email = make_user(f"_test_immo_only_{role.lower()}@example.com", [role])
			with self.subTest(role=role):
				self.assertEqual(frappe.db.get_value("User", email, "user_type"), "Website User")
				frappe.set_user(email)
				frappe.session.data.user_type = "Website User"
				try:
					with self.assertRaises(frappe.PermissionError):
						desk.get_context(frappe._dict())
				finally:
					frappe.set_user("Administrator")


class TestAppPage(IntegrationTestCase):
	def test_app_route_and_sub_routes_resolve_to_the_app_page(self):
		for path in ("sky-immo", "sky-immo/properties", "sky-immo/a/b/c"):
			with self.subTest(path=path):
				set_request(method="GET", path=f"/{path}")
				self.assertEqual(resolve_path(path), "sky_immo")

	def test_guest_gets_the_app_for_its_own_sign_in_screen(self):
		# The app's router shows /sky-immo/connexion; Frappe's /login must not take over.
		for mode in (MODE_SKY, MODE_CUSTOMER):
			for path in ("/sky-immo", "/sky-immo/connexion", "/sky-immo/mot-de-passe-oublie"):
				with self.subTest(mode=mode, path=path):
					set_request(method="GET", path=path)
					frappe.set_user("Guest")
					try:
						with patch.object(sky_immo, "get_operating_mode", return_value=mode):
							context = sky_immo.get_context(frappe._dict())
					finally:
						frappe.set_user("Administrator")

					self.assertEqual(context.boot["session_user"], "Guest")
					self.assertIsNone(context.boot["csrf_token"])

	def test_signed_in_user_gets_boot_data(self):
		email = make_user("_test_immo_page_tenant@example.com", ["Tenant"])
		set_request(method="GET", path="/sky-immo")
		frappe.set_user(email)
		try:
			context = sky_immo.get_context(frappe._dict())
		finally:
			frappe.set_user("Administrator")

		self.assertEqual(context.boot["session_user"], email)
		self.assertTrue(context.boot["csrf_token"])


class TestTranslations(IntegrationTestCase):
	def test_frontend_strings_follow_the_user_language(self):
		compile_translations("skyeng_immo", "fr")
		frappe.cache.delete_value(MERGED_TRANSLATION_KEY)
		original = frappe.local.lang
		try:
			frappe.local.lang = "fr"
			self.assertEqual(get_translations().get("Sign out"), "Se déconnecter")
			frappe.local.lang = "en"
			self.assertNotIn("Sign out", get_translations())
		finally:
			frappe.local.lang = original


class TestUninstall(IntegrationTestCase):
	def test_before_uninstall_drops_the_asset_custom_fields(self):
		expected = {
			frappe.db.get_value("Custom Field", {"dt": "Asset", "fieldname": f["fieldname"]})
			for f in install.ASSET_CUSTOM_FIELDS["Asset"]
		}
		self.assertNotIn(None, expected)

		# Mocked: deleting a Custom Field alters the table, which would commit the test transaction.
		with patch.object(install.frappe, "delete_doc") as delete_doc:
			install.before_uninstall()

		deleted = {call.args[1] for call in delete_doc.call_args_list if call.args[0] == "Custom Field"}
		self.assertEqual(deleted, expected)
