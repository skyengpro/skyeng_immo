from itertools import count
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from propms.tests.utils import create_customer

from skyeng_immo.access import get_scope
from skyeng_immo.immobilier.doctype.sky_immo_settings.test_sky_immo_settings import make_user
from skyeng_immo.invitation import invite_customer
from skyeng_immo.tests.utils import make_lease, make_property

INVITER = "_test_immo_inviter@example.com"
_serial = count(1)


def make_invitee(owns: bool = False, rents: bool = False, email: str | None = "") -> tuple[str, str]:
	"""A Customer with a fresh email, optionally owning a property and renting another."""
	n = next(_serial)
	customer = create_customer(f"_Test Immo Invitee {n}")
	email = f"_test_immo_invitee_{n}@example.com" if email == "" else email
	# Customer.email_id is read from the primary contact; the stored value is what the app reads.
	frappe.db.set_value("Customer", customer, "email_id", email)
	if owns:
		make_property(f"_Test Immo Invite Owned {n}", owner=customer)
	if rents:
		unit = make_property(
			f"_Test Immo Invite Rented {n}", owner=create_customer("_Test Immo Invite Owner")
		)
		lease = make_lease(unit, customer)
		assert frappe.db.get_value("Lease", lease, "lease_status") == "Active"
	return customer, email


def make_outgoing_account() -> None:
	"""A default outgoing account, so mails are queued. Frappe opens no SMTP connection in tests."""
	if not frappe.db.exists("Email Account", "_Test Immo Outgoing"):
		frappe.get_doc(
			{
				"doctype": "Email Account",
				"email_account_name": "_Test Immo Outgoing",
				"email_id": "noreply@example.com",
				"enable_outgoing": 1,
				"default_outgoing": 1,
				"smtp_server": "localhost",
				"smtp_port": 25,
				"no_smtp_authentication": 1,
			}
		).insert(ignore_permissions=True)


def sent_to(email: str) -> list[str]:
	"""Messages queued for `email`."""
	queues = frappe.get_all("Email Queue Recipient", filters={"recipient": email}, pluck="parent")
	return [frappe.db.get_value("Email Queue", q, "message") for q in queues]


class TestInvitation(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Property Manager has no DocPerm on Customer; Sales User is the extra role it needs.
		make_user(INVITER, ["Property Manager", "Sales User"])
		make_outgoing_account()

	def invite(self, customer: str) -> dict:
		with self.set_user(INVITER):
			return invite_customer(customer)

	def test_role_follows_what_the_customer_owns_and_rents(self):
		cases = {
			"landlord": (dict(owns=True), ["Landlord"]),
			"tenant": (dict(rents=True), ["Tenant"]),
			"both": (dict(owns=True, rents=True), ["Landlord", "Tenant"]),
		}
		for label, (kwargs, roles) in cases.items():
			customer, email = make_invitee(**kwargs)
			with self.subTest(case=label):
				self.assertEqual(self.invite(customer)["roles"], roles)
				self.assertTrue(set(roles) <= set(frappe.get_roles(email)))

	def test_new_user_is_linked_scoped_and_emailed_a_password_link(self):
		customer, email = make_invitee(owns=True)
		result = self.invite(customer)

		self.assertTrue(result["created"])
		user = frappe.get_doc("User", email)
		self.assertTrue(user.enabled)
		self.assertEqual(user.user_type, "Website User")
		self.assertEqual(user.default_app, "skyeng_immo")
		self.assertEqual(frappe.get_all("Portal User", {"parent": customer}, pluck="user"), [email])
		# The ERPNext Customer role would open the ERPNext portal beside this app.
		self.assertNotIn("Customer", frappe.get_roles(email))
		self.assertTrue(get_scope(email).owned_properties)

		messages = sent_to(email)
		self.assertEqual(len(messages), 1)
		self.assertIn("/update-password?key=", messages[0])

	def test_existing_user_is_reused_and_keeps_their_roles(self):
		customer, email = make_invitee(owns=True)
		make_user(email, ["Sales User"])

		self.assertFalse(self.invite(customer)["created"])
		self.assertEqual(self.invite(customer)["user"], email)

		self.assertTrue({"Sales User", "Landlord"} <= set(frappe.get_roles(email)))
		self.assertEqual(frappe.get_all("Portal User", {"parent": customer}, pluck="user"), [email])
		self.assertEqual(len(sent_to(email)), 2)

	def test_staff_user_keeps_desk_and_their_default_app(self):
		customer, email = make_invitee(owns=True)
		make_user(email, ["Property Manager"])
		frappe.db.set_value("User", email, "default_app", "")

		self.invite(customer)

		user = frappe.get_doc("User", email)
		self.assertEqual(user.user_type, "System User")
		self.assertFalse(user.default_app)

	def test_refused_without_email_or_without_property_and_lease(self):
		cases = {
			"no email": (make_invitee(owns=True, email=None)[0], "no email address"),
			"nothing owned or rented": (make_invitee()[0], "owns no property and has no active lease"),
		}
		for label, (customer, message) in cases.items():
			with self.subTest(case=label):
				with self.assertRaises(frappe.ValidationError) as raised:
					self.invite(customer)
				self.assertIn(message, str(raised.exception))

	def test_disabled_user_is_refused(self):
		customer, email = make_invitee(owns=True)
		make_user(email, [])
		frappe.db.set_value("User", email, "enabled", 0)

		with self.assertRaises(frappe.ValidationError) as raised:
			self.invite(customer)
		self.assertIn("is disabled", str(raised.exception))
		self.assertFalse(sent_to(email))

	def test_missing_outgoing_email_account_is_reported(self):
		customer, email = make_invitee(owns=True)
		with patch(
			"frappe.core.doctype.user.user.User.send_welcome_mail_to_user",
			side_effect=frappe.OutgoingEmailError,
		):
			with self.assertRaises(frappe.ValidationError) as raised:
				self.invite(customer)
		self.assertIn("No outgoing email account", str(raised.exception))

	def test_only_staff_who_can_read_the_customer_may_invite(self):
		customer, email = make_invitee(owns=True)
		outsiders = {
			"landlord": make_user("_test_immo_invite_landlord@example.com", ["Landlord"]),
			"tenant": make_user("_test_immo_invite_tenant@example.com", ["Tenant"]),
			"sales user": make_user("_test_immo_invite_sales@example.com", ["Sales User"]),
			# Staff role but no read access to Customer.
			"manager alone": make_user("_test_immo_invite_alone@example.com", ["Property Manager"]),
		}
		for label, user in outsiders.items():
			with self.subTest(user=label), self.set_user(user):
				with self.assertRaises(frappe.PermissionError):
					invite_customer(customer)
		self.assertFalse(frappe.db.exists("User", email))
