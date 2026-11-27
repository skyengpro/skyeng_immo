"""Demo data for presenting Sky Immo on a development site: two landlords, three tenants.

    bench --site <site> execute skyeng_immo.sky_immo.demo.create_demo_data
    bench --site <site> execute skyeng_immo.sky_immo.demo.delete_demo_data

Every record is named with the DEMO prefix and removed by ``delete_demo_data``.
Accounts (password ``demo1234``):

=================================  ===========================================
gestionnaire.demo@example.com      Property Manager: every property, by landlord
emmanuel.fotso@example.com         Landlord: Résidence Les Palmiers (4 units)
marie.ndjock@example.com           Landlord: Villa Bastos
clarisse.ngo@example.com           Tenant, up to date
herve.kamga@example.com            Tenant, one invoice 20 days late
sandrine.mbarga@example.com        Tenant of the second landlord
=================================  ===========================================

Refuses to run unless the site is in developer mode.
"""

import frappe
from frappe import _
from frappe.utils import add_days, add_months, get_first_day, get_last_day, getdate, today
from frappe.utils.password import update_password

PREFIX = "DEMO"
PASSWORD = "demo1234"

LANDLORDS = {
	"fotso": ("DEMO Emmanuel Fotso", "emmanuel.fotso@example.com", "fr"),
	"ndjock": ("DEMO Marie Ndjock", "marie.ndjock@example.com", "fr"),
}
TENANTS = {
	"clarisse": ("DEMO Clarisse Ngo Nlend", "clarisse.ngo@example.com", "fr"),
	"herve": ("DEMO Hervé Kamga", "herve.kamga@example.com", "en"),
	"sandrine": ("DEMO Sandrine Mbarga", "sandrine.mbarga@example.com", "fr"),
}
MANAGER = "gestionnaire.demo@example.com"


def _guard():
	if not frappe.conf.developer_mode:
		frappe.throw(_("Demo data is only for development sites (developer_mode)."))


def _leaf(doctype):
	return frappe.get_all(doctype, filters={"is_group": 0}, pluck="name", limit=1)[0]


def _company():
	return frappe.defaults.get_global_default("company")


def _customer(name, email, lang):
	if frappe.db.exists("Customer", name):
		return name
	return (
		frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_group": _leaf("Customer Group"),
				"territory": _leaf("Territory"),
				"language": lang,
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def _user(email, first, last, role, lang, customer=None):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first,
				"last_name": last,
				"language": lang,
				"send_welcome_email": 0,
				"roles": [{"role": role}],
			}
		).insert(ignore_permissions=True)
	update_password(email, PASSWORD)
	if customer:
		doc = frappe.get_doc("Customer", customer)
		if not any(row.user == email for row in doc.portal_users):
			doc.append("portal_users", {"user": email})
			doc.save(ignore_permissions=True)


def _item(code):
	if not frappe.db.exists("Item", code):
		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": code,
				"item_group": _leaf("Item Group"),
				"is_stock_item": 0,
				"stock_uom": "Nos",
			}
		).insert(ignore_permissions=True)
	return code


def _property(name, owner, parent=None, is_group=0, **fields):
	if frappe.db.exists("Property", name):
		return name
	doc = frappe.get_doc(
		{
			"doctype": "Property",
			"name1": name,
			"unit_owner": owner,
			"parent_property": parent,
			"is_group": is_group,
			"company": _company(),
			**fields,
		}
	)
	doc.flags.ignore_mandatory = True
	return doc.insert(ignore_permissions=True).name


def _lease(prop, customer, start, end, frequency, lines, deposit):
	existing = frappe.db.get_value("Lease", {"property": prop, "customer": customer})
	if existing:
		return existing
	return (
		frappe.get_doc(
			{
				"doctype": "Lease",
				"company": _company(),
				"property": prop,
				"customer": customer,
				"lease_customer": customer,
				"start_date": start,
				"end_date": end,
				"frequency": frequency,
				"lease_status": "Active",
				"notice_period": 30,
				"security_deposit": deposit,
				"security_status": "Received",
				"lease_item": [
					{"lease_item": item, "amount": amount, "frequency": frequency, "paid_by": customer}
					for item, amount in lines
				],
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


def _bill(lease_name, period_start, months, pay_on=None, due_in_days=5):
	"""Invoice one period of a lease, link it in the lease schedule, optionally pay it."""
	lease = frappe.get_doc("Lease", lease_name)
	period_start = getdate(period_start)
	period_end = get_last_day(add_months(period_start, months - 1))
	posting = add_days(period_start, -10)
	income = frappe.get_all(
		"Account",
		filters={"company": _company(), "root_type": "Income", "is_group": 0},
		pluck="name",
		limit=1,
	)[0]
	invoice = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": lease.customer,
			"company": _company(),
			"set_posting_time": 1,
			"posting_date": posting,
			"due_date": add_days(period_start, due_in_days),
			"from_date": period_start,
			"to_date": period_end,
			"lease": lease.name,
			"items": [
				{"item_code": row.lease_item, "qty": months, "rate": row.amount, "income_account": income}
				for row in lease.lease_item
			],
		}
	)
	invoice.insert(ignore_permissions=True)
	invoice.submit()
	for row in lease.lease_item:
		lease.append(
			"lease_invoice_schedule",
			{
				"date_to_invoice": posting,
				"schedule_start_date": period_start,
				"lease_item": row.lease_item,
				"paid_by": lease.customer,
				"qty": months,
				"rate": row.amount,
				"invoice_number": invoice.name,
				"document_type": "Sales Invoice",
			},
		)
	lease.save(ignore_permissions=True)

	if pay_on:
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		pe = get_payment_entry("Sales Invoice", invoice.name)
		pe.posting_date = pay_on
		pe.reference_no = f"{PREFIX}-{invoice.name}"
		pe.reference_date = pay_on
		pe.insert(ignore_permissions=True)
		pe.submit()
	return invoice.name


def create_demo_data():
	_guard()
	from skyeng_immo.install import setup

	setup()
	frappe.flags.mute_emails = True
	rent = _item("DEMO Loyer")
	charges = _item("DEMO Charges")

	owners = {key: _customer(name, email, lang) for key, (name, email, lang) in LANDLORDS.items()}
	tenants = {key: _customer(name, email, lang) for key, (name, email, lang) in TENANTS.items()}

	building = _property("DEMO Résidence Les Palmiers", owners["fotso"], is_group=1)
	a1 = _property(
		"DEMO Palmiers A1",
		owners["fotso"],
		building,
		bedroom=2,
		common_bathroom=1,
		builtup_area=85,
		rent=150000,
	)
	a2 = _property(
		"DEMO Palmiers A2",
		owners["fotso"],
		building,
		bedroom=1,
		common_bathroom=1,
		builtup_area=60,
		rent=110000,
	)
	_property(
		"DEMO Palmiers B1",
		owners["fotso"],
		building,
		bedroom=1,
		common_bathroom=1,
		builtup_area=40,
		rent=80000,
	)
	_property(
		"DEMO Palmiers B2",
		owners["fotso"],
		building,
		bedroom=2,
		common_bathroom=1,
		builtup_area=70,
		rent=120000,
	)
	villa = _property(
		"DEMO Villa Bastos",
		owners["ndjock"],
		bedroom=4,
		common_bathroom=3,
		builtup_area=240,
		furnished=1,
		rent=300000,
	)

	this_month = get_first_day(today())
	# Stay inside the current fiscal year: at most six months back.
	months_back = min(6, getdate(today()).month - 1)
	start = add_months(this_month, -months_back)
	end = add_days(add_months(start, 24), -1)

	if not frappe.db.exists("Lease", {"property": a1}):
		l1 = _lease(
			a1, tenants["clarisse"], start, end, "Monthly", [(rent, 150000), (charges, 15000)], 300000
		)
		# Clarisse is up to date: every month paid three days after it starts.
		for i in range(months_back + 1):
			period = add_months(start, i)
			paid_on = add_days(period, 3)
			_bill(l1, period, 1, pay_on=paid_on if getdate(paid_on) <= getdate(today()) else None)

		l2 = _lease(a2, tenants["herve"], start, end, "Quarterly", [(rent, 110000)], 220000)
		# Quarters that started at least 30 days ago; the latest one stays unpaid.
		periods = [
			i for i in range(0, months_back + 1, 3) if add_months(start, i) <= getdate(add_days(today(), -30))
		]
		for n, i in enumerate(periods):
			period = add_months(start, i)
			last = n == len(periods) - 1
			# The latest quarter stays unpaid, 20 days past due.
			due_in = (getdate(today()) - getdate(period)).days - 20 if last else 5
			_bill(l2, period, 3, pay_on=None if last else add_days(period, 4), due_in_days=due_in)

		l3 = _lease(villa, tenants["sandrine"], start, end, "Monthly", [(rent, 300000)], 600000)
		# Sandrine has paid every past month; this month's rent is due in a few days.
		for i in range(months_back + 1):
			period = add_months(start, i)
			current = period >= this_month
			due_in = (getdate(today()) - getdate(period)).days + 6 if current else 5
			_bill(l3, period, 1, pay_on=None if current else add_days(period, 2), due_in_days=due_in)

	_user(MANAGER, "Gestionnaire", "Démo", "Property Manager", "fr")
	_user(LANDLORDS["fotso"][1], "Emmanuel", "Fotso", "Landlord", "fr", owners["fotso"])
	_user(LANDLORDS["ndjock"][1], "Marie", "Ndjock", "Landlord", "fr", owners["ndjock"])
	_user(TENANTS["clarisse"][1], "Clarisse", "Ngo Nlend", "Tenant", "fr", tenants["clarisse"])
	_user(TENANTS["herve"][1], "Hervé", "Kamga", "Tenant", "en", tenants["herve"])
	_user(TENANTS["sandrine"][1], "Sandrine", "Mbarga", "Tenant", "fr", tenants["sandrine"])

	if not frappe.db.exists("Issue", {"customer": tenants["clarisse"]}):
		issue = frappe.get_doc(
			{
				"doctype": "Issue",
				"subject": "Le climatiseur de la chambre ne refroidit plus",
				"description": "Depuis hier soir, il souffle de l'air chaud.",
				"raised_by": TENANTS["clarisse"][1],
				"customer": tenants["clarisse"],
				"property_name": a1,
				"company": _company(),
				"issue_type": "Climatisation",
				"priority": "Medium",
				"status": "Open",
			}
		)
		issue.flags.ignore_mandatory = True
		issue.insert(ignore_permissions=True)
		# Valid on both ERPNext's and PropMS's status lists.
		in_progress = (
			"In Progress"
			if "In Progress" in (frappe.get_meta("Issue").get_options("status") or "")
			else "Replied"
		)
		issue.db_set("status", in_progress)

	# No commit here: `bench execute` (the documented way to run this) commits once it returns.
	print("Sky Immo demo data ready. Password for every account:", PASSWORD)


def delete_demo_data():
	_guard()
	frappe.flags.mute_emails = True
	# Each lookup runs only on names found: Frappe reads `x in []` (or `in [""]`) as "x not set",
	# which would select every invoice without a lease and every request without a customer.
	customers = frappe.get_all("Customer", filters={"name": ["like", f"{PREFIX} %"]}, pluck="name")
	leases = (
		frappe.get_all("Lease", filters={"customer": ["in", customers]}, pluck="name") if customers else []
	)
	invoices = (
		frappe.get_all("Sales Invoice", filters={"lease": ["in", leases]}, pluck="name") if leases else []
	)
	payments = (
		frappe.get_all(
			"Payment Entry Reference",
			filters={"reference_doctype": "Sales Invoice", "reference_name": ["in", invoices]},
			pluck="parent",
		)
		if invoices
		else []
	)
	for name in set(payments):
		doc = frappe.get_doc("Payment Entry", name)
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Payment Entry", name, force=True, ignore_permissions=True)
	for name in invoices:
		doc = frappe.get_doc("Sales Invoice", name)
		if doc.docstatus == 1:
			doc.cancel()
		frappe.delete_doc("Sales Invoice", name, force=True, ignore_permissions=True)
	issues = (
		frappe.get_all("Issue", filters={"customer": ["in", customers]}, pluck="name") if customers else []
	)
	for name in issues:
		frappe.delete_doc("Issue", name, force=True, ignore_permissions=True)
	for name in leases:
		frappe.delete_doc("Lease", name, force=True, ignore_permissions=True)
	# Units before buildings.
	for name in frappe.get_all(
		"Property", filters={"name": ["like", f"{PREFIX} %"]}, pluck="name", order_by="lft desc"
	):
		frappe.delete_doc("Property", name, force=True, ignore_permissions=True)
	for email in [MANAGER, *(v[1] for v in LANDLORDS.values()), *(v[1] for v in TENANTS.values())]:
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
	for name in customers:
		frappe.delete_doc("Customer", name, force=True, ignore_permissions=True)
	for code in ("DEMO Loyer", "DEMO Charges"):
		if frappe.db.exists("Item", code):
			frappe.delete_doc("Item", code, force=True, ignore_permissions=True)
	print("Sky Immo demo data removed.")
