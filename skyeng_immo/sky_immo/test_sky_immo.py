"""Sky Immo access rules and screens, on a site with two landlords (EP-01 definition of done).

Run with: ``CI=1 bench --site <site> run-tests --module skyeng_immo.sky_immo.test_sky_immo``
Everything is created inside the test transaction and rolled back.
"""

import base64

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, add_months, get_first_day, getdate, today

from skyeng_immo.sky_immo import api
from skyeng_immo.sky_immo.access import app_role, get_scope
from skyeng_immo.sky_immo.invite import invite_to_app
from skyeng_immo.sky_immo.notifications import send_due_reminders, send_payment_emails

PREFIX = "MI-TEST"
# 1×1 transparent PNG.
PIXEL = (
	"data:image/png;base64,"
	"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def _leaf(doctype: str) -> str:
	return frappe.get_all(doctype, filters={"is_group": 0}, pluck="name", limit=1)[0]


def _customer(name: str) -> str:
	return (
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": f"{PREFIX} {name}",
				"customer_group": _leaf("Customer Group"),
				"territory": _leaf("Territory"),
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def _user(email: str, role: str, customer: str | None = None) -> str:
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": email.split("@")[0],
			"send_welcome_email": 0,
			"roles": [{"role": role}],
		}
	).insert(ignore_permissions=True)
	if customer:
		doc = frappe.get_doc("Customer", customer)
		doc.append("portal_users", {"user": user.name})
		doc.save(ignore_permissions=True)
	return user.name


def _property(name: str, owner: str | None, parent: str | None = None, is_group: int = 0) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Property",
			"name1": f"{PREFIX} {name}",
			"unit_owner": owner,
			"parent_property": parent,
			"is_group": is_group,
			"company": frappe.defaults.get_global_default("company"),
			"rent": 100000,
		}
	)
	doc.flags.ignore_mandatory = True
	return doc.insert(ignore_permissions=True).name


def _lease(prop: str, customer: str, item: str) -> str:
	return (
		frappe.get_doc(
			{
				"doctype": "Lease",
				"company": frappe.defaults.get_global_default("company"),
				"property": prop,
				"customer": customer,
				"lease_customer": customer,
				"start_date": add_days(today(), -60),
				"end_date": add_days(today(), 300),
				"frequency": "Monthly",
				"lease_status": "Active",
				"notice_period": 30,
				"security_deposit": 200000,
				"security_status": "Received",
				"lease_item": [{"lease_item": item, "amount": 100000, "frequency": "Monthly"}],
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def _invoice(customer: str, lease: str, item: str, income: str, due_days: int) -> str:
	company = frappe.defaults.get_global_default("company")
	posting = add_days(today(), due_days - 10)
	doc = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": customer,
			"company": company,
			"set_posting_time": 1,
			"posting_date": posting,
			"due_date": add_days(today(), due_days),
			"lease": lease,
			"items": [{"item_code": item, "qty": 1, "rate": 100000, "income_account": income}],
		}
	)
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


def _pay(invoice: str) -> str:
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

	pe = get_payment_entry("Sales Invoice", invoice)
	pe.posting_date = today()
	pe.reference_no = f"{PREFIX}-REF"
	pe.reference_date = today()
	pe.insert(ignore_permissions=True)
	pe.submit()
	return pe.name


class TestSkyImmo(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		from skyeng_immo.install import setup

		setup()
		if not frappe.db.exists("Email Account", {"default_outgoing": 1, "enable_outgoing": 1}):
			frappe.get_doc(
				{
					"doctype": "Email Account",
					"email_account_name": f"{PREFIX} outgoing",
					"email_id": "mi-outgoing@example.com",
					"enable_outgoing": 1,
					"default_outgoing": 1,
					"smtp_server": "localhost",
					"no_smtp_authentication": 1,
				}
			).insert(ignore_permissions=True)
		company = frappe.defaults.get_global_default("company")
		cls.income = frappe.get_all(
			"Account",
			filters={"company": company, "root_type": "Income", "is_group": 0},
			pluck="name",
			limit=1,
		)[0]
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": f"{PREFIX} Rent",
				"item_group": _leaf("Item Group"),
				"is_stock_item": 0,
				"stock_uom": "Nos",
			}
		)
		cls.item = item.insert(ignore_permissions=True).name

		cls.landlord_a = _customer("Landlord A")
		cls.landlord_b = _customer("Landlord B")
		cls.tenant_1 = _customer("Tenant 1")
		cls.tenant_2 = _customer("Tenant 2")

		# Landlord A owns a building; its units are recorded under A too (unit_owner always set).
		cls.building_a = _property("Building A", cls.landlord_a, is_group=1)
		cls.unit_a1 = _property("A1", cls.landlord_a, parent=cls.building_a)
		cls.unit_a2 = _property("A2", cls.landlord_a, parent=cls.building_a)
		cls.unit_b1 = _property("B1", cls.landlord_b)

		cls.lease_1 = _lease(cls.unit_a1, cls.tenant_1, cls.item)
		cls.lease_2 = _lease(cls.unit_b1, cls.tenant_2, cls.item)

		cls.inv_late = _invoice(cls.tenant_1, cls.lease_1, cls.item, cls.income, due_days=-20)
		cls.inv_paid = _invoice(cls.tenant_1, cls.lease_1, cls.item, cls.income, due_days=-5)
		cls.payment = _pay(cls.inv_paid)
		cls.inv_b = _invoice(cls.tenant_2, cls.lease_2, cls.item, cls.income, due_days=5)

		cls.user_a = _user("mi-landlord-a@example.com", "Landlord", cls.landlord_a)
		cls.user_b = _user("mi-landlord-b@example.com", "Landlord", cls.landlord_b)
		cls.user_t1 = _user("mi-tenant-1@example.com", "Tenant", cls.tenant_1)
		cls.user_t2 = _user("mi-tenant-2@example.com", "Tenant", cls.tenant_2)
		cls.user_pm = _user("mi-manager@example.com", "Property Manager")

	def tearDown(self):
		frappe.set_user("Administrator")

	def as_user(self, user):
		frappe.set_user(user)
		frappe.local.response = frappe._dict()

	# ------------------------------------------------------------------ roles

	def test_roles_pick_the_space(self):
		self.assertEqual(app_role(self.user_a), "owner")
		self.assertEqual(app_role(self.user_t1), "tenant")
		self.assertEqual(app_role(self.user_pm), "manager")
		self.assertIsNone(app_role("Guest"))

	def test_desk_icon_for_every_app_user(self):
		from frappe.apps import get_apps

		from skyeng_immo.sky_immo.access import has_app_permission

		for user in (self.user_pm, self.user_a, self.user_t1):
			self.as_user(user)
			self.assertTrue(has_app_permission(), user)
		route = next(app["route"] for app in get_apps() if app["name"] == "skyeng_immo")
		self.assertEqual(route, "/sky-immo")
		self.as_user("Guest")
		self.assertFalse(has_app_permission())

	def test_session(self):
		self.as_user(self.user_t1)
		session = api.get_session()
		self.assertEqual(session["user"]["role"], "tenant")
		self.assertTrue(session["csrfToken"])

	# ------------------------------------------------------------ landlords

	def test_each_landlord_sees_only_their_properties(self):
		self.as_user(self.user_a)
		scope = get_scope()
		self.assertEqual(
			{p for p in scope.properties() if p.startswith(PREFIX)},
			{self.building_a, self.unit_a1, self.unit_a2},
		)
		units = [
			unit["id"]
			for section in api.list_properties()["sections"]
			for group in section["groups"]
			for unit in group["units"]
		]
		self.assertIn(self.unit_a1, units)
		self.assertNotIn(self.unit_b1, units)

		with self.assertRaises(frappe.DoesNotExistError):
			api.get_property(self.unit_b1)
		with self.assertRaises(frappe.DoesNotExistError):
			api.get_lease(self.lease_2)
		with self.assertRaises(frappe.DoesNotExistError):
			api.get_invoice(self.inv_b)

		self.as_user(self.user_b)
		self.assertNotIn(self.unit_a1, get_scope().properties())
		with self.assertRaises(frappe.DoesNotExistError):
			api.get_property(self.unit_a1)

	def test_building_access_covers_units(self):
		# A unit recorded under another owner still shows for the building's owner.
		frappe.db.savepoint("building_access")
		try:
			unit = _property("A9", self.landlord_b, parent=self.building_a)
			self.as_user(self.user_a)
			self.assertIn(unit, get_scope().properties())
		finally:
			frappe.db.rollback(save_point="building_access")

	def test_landlord_dashboard(self):
		self.as_user(self.user_a)
		data = api.get_owner_dashboard()
		self.assertEqual(data["stats"]["properties"], 2)  # A1 and A2, the building is not a unit
		self.assertEqual(data["stats"]["tenants"], 1)
		self.assertEqual(data["stats"]["unpaidTotal"], 100000)
		self.assertEqual(data["stats"]["collectedThisMonth"], 100000)
		self.assertEqual([inv["id"] for inv in data["overdue"]], [self.inv_late])
		self.assertEqual(data["overdue"][0]["leaseId"], self.lease_1)
		self.assertEqual(data["overdue"][0]["daysLate"], 20)

	def test_property_and_tenant_screens(self):
		self.as_user(self.user_a)
		prop = api.get_property(self.unit_a1)
		self.assertEqual(prop["status"], "let")
		self.assertEqual(prop["currentLease"]["id"], self.lease_1)
		self.assertEqual(prop["currentLease"]["deposit"], {"amount": 200000, "status": "received"})
		self.assertEqual({inv["id"] for inv in prop["invoices"]}, {self.inv_late, self.inv_paid})

		lease = api.get_lease(self.lease_1)
		self.assertEqual([inv["id"] for inv in lease["invoicesDue"]], [self.inv_late])
		self.assertEqual([p["id"] for p in lease["payments"]], [self.payment])
		self.assertEqual(lease["amountPerPeriod"], 100000)
		self.assertTrue(any(line["status"] == "upcoming" for line in lease["schedule"]))

	def test_manager_sees_every_property_grouped_by_landlord(self):
		self.as_user(self.user_pm)
		data = api.list_properties()
		self.assertTrue(data["byLandlord"])
		landlords = {section["landlord"]["id"] for section in data["sections"] if section["landlord"]}
		self.assertTrue({self.landlord_a, self.landlord_b} <= landlords)
		self.assertTrue(api.get_property(self.unit_b1))

	def test_tenant_cannot_open_landlord_screens(self):
		self.as_user(self.user_t1)
		with self.assertRaises(frappe.PermissionError):
			api.get_owner_dashboard()
		with self.assertRaises(frappe.PermissionError):
			api.list_properties()

	def test_account_without_role_has_no_access(self):
		self.as_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			api.get_lease(self.lease_1)

	# --------------------------------------------------------------- tenants

	def test_tenant_home_and_invoices(self):
		self.as_user(self.user_t1)
		home = api.get_tenant_home()
		self.assertEqual(home["balanceDue"], 100000)
		self.assertEqual(home["next"]["invoice"]["id"], self.inv_late)
		self.assertEqual([h["leaseId"] for h in home["homes"]], [self.lease_1])

		self.assertEqual([inv["id"] for inv in api.list_invoices("unpaid")], [self.inv_late])
		self.assertEqual([inv["id"] for inv in api.list_invoices("paid")], [self.inv_paid])
		detail = api.get_invoice(self.inv_paid)
		self.assertEqual(detail["status"], "paid")
		self.assertEqual(detail["payments"][0]["id"], self.payment)

		with self.assertRaises(frappe.DoesNotExistError):
			api.get_invoice(self.inv_b)
		with self.assertRaises(frappe.DoesNotExistError):
			api.get_lease(self.lease_2)
		with self.assertRaises(frappe.DoesNotExistError):
			api.download("receipt", "does-not-exist")

	def test_tenant_up_to_date_sees_the_next_period(self):
		"""Regression: invoiced periods must not come back as "upcoming" on the tenant home."""
		frappe.db.savepoint("up_to_date")
		self.addCleanup(frappe.db.rollback, save_point="up_to_date")
		tenant = _customer("Tenant 4")
		user = _user("mi-tenant-4@example.com", "Tenant", tenant)
		unit = _property("A4", self.landlord_a, parent=self.building_a)
		lease = _lease(unit, tenant, self.item)
		start = getdate(frappe.db.get_value("Lease", lease, "start_date"))
		this_month = get_first_day(today())
		doc = frappe.get_doc("Lease", lease)
		period = get_first_day(start)
		while period <= this_month:
			invoice = _invoice(tenant, lease, self.item, self.income, due_days=-1)
			_pay(invoice)
			doc.append(
				"lease_invoice_schedule",
				{
					"schedule_start_date": period,
					"date_to_invoice": period,
					"lease_item": self.item,
					"qty": 1,
					"rate": 100000,
					"invoice_number": invoice,
				},
			)
			period = getdate(add_months(period, 1))
		doc.save(ignore_permissions=True)

		self.as_user(user)
		home = api.get_tenant_home()
		self.assertEqual(home["balanceDue"], 0)
		self.assertEqual(home["next"]["kind"], "schedule")
		self.assertEqual(home["next"]["line"]["periodStart"], str(add_months(this_month, 1)))

	def test_maintenance_request_with_photos(self):
		self.as_user(self.user_t1)
		created = api.create_issue(
			category="plumbing",
			description="Sous l'évier <script>x</script>",
			urgent=1,
			photos=[PIXEL, PIXEL],
		)
		issue = frappe.get_doc("Issue", created["id"])
		self.assertEqual(issue.property_name, self.unit_a1)
		# the customer is written directly (ERPNext clears it for Website Users)
		self.assertEqual(issue.customer, self.tenant_1)
		self.assertEqual(issue.raised_by, "mi-tenant-1@example.com")
		self.assertEqual(issue.sky_immo_status, "Awaiting approval")
		self.assertEqual(issue.issue_type, "Plomberie")
		self.assertNotIn("<script>", issue.description)

		files = frappe.get_all("File", filters={"attached_to_doctype": "Issue", "attached_to_name": issue.name}, fields=["is_private"])
		self.assertEqual(len(files), 2)
		self.assertTrue(all(f.is_private for f in files))

		detail = api.get_issue(created["id"])
		self.assertTrue(detail["urgent"])
		self.assertEqual(len(detail["photos"]), 2)
		self.assertEqual(detail["approval"], "awaiting_approval")
		self.assertFalse(detail["canComplete"])
		api.issue_photo(created["id"], detail["photos"][1]["id"])
		self.assertEqual(frappe.local.response.filecontent[:4], b"\x89PNG")
		self.assertEqual(api.get_tenant_home()["latestIssue"]["id"], created["id"])

		# another tenant sees nothing, and the photos answer 403
		self.as_user(self.user_t2)
		with self.assertRaises(frappe.DoesNotExistError):
			api.get_issue(created["id"])
		with self.assertRaises(frappe.PermissionError):
			api.issue_photo(created["id"])
		self.assertFalse([i for i in api.list_issues() if i["id"] == created["id"]])

	def test_title_is_optional_description_is_not(self):
		self.as_user(self.user_t1)
		with self.assertRaises(frappe.ValidationError):
			api.create_issue(description="   ")
		created = api.create_issue(description="La porte ne ferme plus\nDepuis lundi")
		self.assertEqual(frappe.db.get_value("Issue", created["id"], "subject"), "La porte ne ferme plus")

	def test_photos_are_limited_and_must_be_images(self):
		self.as_user(self.user_t1)
		with self.assertRaises(frappe.ValidationError) as caught:
			api.create_issue(description="x", photos=[PIXEL, PIXEL, PIXEL])
		self.assertIn("2", str(caught.exception))
		with self.assertRaises(frappe.ValidationError) as caught:
			api.create_issue(description="x", photos=["data:text/html;base64,PGI+"])
		self.assertIn("not an image", str(caught.exception))
		big = "data:image/png;base64," + base64.b64encode(b"\0" * (5 * 1024 * 1024 + 1)).decode()
		with self.assertRaises(frappe.ValidationError) as caught:
			api.create_issue(description="x", photos=[big])
		self.assertIn("5 MB", str(caught.exception))
		# nothing was written by the refused requests
		self.assertFalse(frappe.db.exists("Issue", {"raised_by": "mi-tenant-1@example.com", "subject": "x"}))

	def test_request_only_on_a_unit_of_an_active_lease(self):
		self.as_user(self.user_t1)
		with self.assertRaises(frappe.PermissionError):
			api.create_issue(description="x", property=self.unit_b1)
		with self.assertRaises(frappe.PermissionError):
			api.create_issue(description="x", property=self.unit_a2)

	def test_tenant_closes_a_request_only_when_in_progress(self):
		from skyeng_immo.sky_immo import maintenance

		self.as_user(self.user_t1)
		name = api.create_issue(description="Fuite")["id"]
		# still awaiting approval: cannot be completed
		with self.assertRaises(frappe.ValidationError):
			api.complete_issue(name)

		# the owner approves it
		self.as_user(self.user_a)
		api.decide_issue(name, "approve")

		# another tenant cannot close it
		self.as_user(self.user_t2)
		with self.assertRaises(frappe.PermissionError):
			api.complete_issue(name)
		# neither can the landlord
		self.as_user(self.user_a)
		with self.assertRaises(frappe.PermissionError):
			api.complete_issue(name)

		self.as_user(self.user_t1)
		self.assertTrue(api.get_issue(name)["canComplete"])
		self.assertEqual(api.complete_issue(name)["approval"], "completed")
		self.assertEqual(frappe.db.get_value("Issue", name, ["sky_immo_status", "status"]), ("Completed", "Resolved"))
		# once completed, it cannot be completed again
		with self.assertRaises(frappe.ValidationError):
			api.complete_issue(name)
		self.assertFalse(maintenance.can_complete(name, self.user_t1))

	def test_next_due_is_the_oldest_unpaid_invoice(self):
		self.as_user(self.user_t1)
		home = api.get_tenant_home()
		self.assertEqual(home["next"]["kind"], "invoice")
		self.assertEqual(home["next"]["invoice"]["id"], self.inv_late)

	# ------------------------------------------------------- desk-side rules

	def test_property_needs_an_owner(self):
		with self.assertRaises(frappe.ValidationError):
			_property("No owner", None)

	def test_lease_has_a_single_customer(self):
		lease = frappe.get_doc("Lease", self.lease_1)
		lease.lease_item[0].paid_by = self.tenant_2
		with self.assertRaises(frappe.ValidationError):
			lease.save(ignore_permissions=True)

	def test_invite_creates_the_account_and_link(self):
		result = invite_to_app(self.tenant_2, "mi-invited@example.com", "Tenant", "en")
		self.assertTrue(result["created"])
		self.assertTrue(result["invitationSent"])
		self.assertIn("Tenant", frappe.get_roles("mi-invited@example.com"))
		self.assertEqual(frappe.db.get_value("User", "mi-invited@example.com", "user_type"), "Website User")
		self.assertEqual(frappe.db.get_value("User", "mi-invited@example.com", "default_app"), "skyeng_immo")
		self.assertIn(
			"mi-invited@example.com",
			[row.user for row in frappe.get_doc("Customer", self.tenant_2).portal_users],
		)
		frappe.set_user(self.user_t1)
		with self.assertRaises(frappe.PermissionError):
			invite_to_app(self.tenant_1, "mi-other@example.com", "Landlord")

	# ---------------------------------------------------------------- emails

	def test_payment_emails_reach_tenant_and_landlord(self):
		frappe.db.delete(
			"Email Queue", {"reference_doctype": "Payment Entry", "reference_name": self.payment}
		)
		send_payment_emails(self.payment)
		queued = frappe.get_all(
			"Email Queue",
			filters={"reference_doctype": "Payment Entry", "reference_name": self.payment},
			fields=["name", "attachments"],
		)
		recipients = set(
			frappe.get_all(
				"Email Queue Recipient",
				filters={"parent": ["in", [q.name for q in queued]]},
				pluck="recipient",
			)
		)
		self.assertEqual(recipients, {self.user_t1, self.user_a})
		# The tenant's receipt carries the PDF; the landlord's notice does not.
		self.assertEqual(sum(1 for q in queued if q.attachments and q.attachments != "[]"), 1)

	def test_due_reminder(self):
		frappe.db.set_value("Sales Invoice", self.inv_b, "due_date", add_days(today(), 5))
		send_due_reminders()
		queued = frappe.get_all(
			"Email Queue",
			filters={"reference_doctype": "Sales Invoice", "reference_name": self.inv_b},
			pluck="name",
		)
		self.assertEqual(len(queued), 1)
		self.assertEqual(
			frappe.get_all("Email Queue Recipient", filters={"parent": queued[0]}, pluck="recipient"),
			[self.user_t2],
		)

	def test_one_payment_for_two_landlords_stays_separated(self):
		"""A tenant renting from A and B settles both invoices in one Payment Entry."""
		frappe.db.savepoint("shared_payment")
		self.addCleanup(frappe.db.rollback, save_point="shared_payment")
		tenant = _customer("Tenant 3")
		unit_a3 = _property("A3", self.landlord_a, parent=self.building_a)
		unit_b2 = _property("B2", self.landlord_b)
		lease_a = _lease(unit_a3, tenant, self.item)
		lease_b = _lease(unit_b2, tenant, self.item)
		inv_a = _invoice(tenant, lease_a, self.item, self.income, due_days=5)
		inv_b = _invoice(tenant, lease_b, self.item, self.income, due_days=5)

		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		pe = get_payment_entry("Sales Invoice", inv_a)
		pe.append(
			"references",
			{
				"reference_doctype": "Sales Invoice",
				"reference_name": inv_b,
				"total_amount": 100000,
				"outstanding_amount": 100000,
				"allocated_amount": 100000,
			},
		)
		pe.paid_amount = pe.received_amount = 200000
		pe.reference_no, pe.reference_date = f"{PREFIX}-BOTH", today()
		pe.insert(ignore_permissions=True)
		pe.submit()

		# Landlord A sees the payment on their invoice, but not a receipt naming B's invoice.
		self.as_user(self.user_a)
		lease = api.get_lease(lease_a)
		self.assertEqual([(p["id"], p["amount"]) for p in lease["payments"]], [(pe.name, 100000)])
		with self.assertRaises(frappe.DoesNotExistError):
			api.download("receipt", pe.name)

		# Each landlord's notice names only their own invoice and amount.
		frappe.set_user("Administrator")
		frappe.db.delete("Email Queue", {"reference_doctype": "Payment Entry", "reference_name": pe.name})
		send_payment_emails(pe.name)
		seen = set()
		for queue in frappe.get_all(
			"Email Queue",
			filters={"reference_doctype": "Payment Entry", "reference_name": pe.name},
			fields=["name", "message"],
		):
			recipients = frappe.get_all(
				"Email Queue Recipient", filters={"parent": queue.name}, pluck="recipient"
			)
			if recipients == [self.user_a]:
				seen.add("a")
				self.assertIn(inv_a, queue.message)
				self.assertNotIn(inv_b, queue.message)
			if recipients == [self.user_b]:
				seen.add("b")
				self.assertIn(inv_b, queue.message)
				self.assertNotIn(inv_a, queue.message)
		self.assertEqual(seen, {"a", "b"})
