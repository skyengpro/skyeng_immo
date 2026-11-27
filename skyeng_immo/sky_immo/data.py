"""Read models for the app screens, built from PropMS and ERPNext records.

Nothing here checks permissions: callers pass names that already went
through :func:`skyeng_immo.access.get_scope`. Reads use ``ignore_permissions``
because landlords and tenants have no doctype permission at all.
"""

from collections import defaultdict
from datetime import date

import frappe
from frappe.query_builder import DocType
from frappe.utils import add_months, date_diff, flt, get_first_day, get_last_day, getdate, today

# PropMS frequency → app key, and its length in months.
FREQUENCIES = {
	"Monthly": ("monthly", 1),
	"Bi-Monthly": ("bimonthly", 2),
	"Quarterly": ("quarterly", 3),
	"6 months": ("semiannual", 6),
	"Annually": ("annual", 12),
}

ENDING_SOON_DAYS = 90

LEASE_STATUS = {
	"Active": "active",
	"Renewal to Previous Lease": "active",
	"Adendum to Previous Lease": "active",
	"Vacating": "notice_given",
	"Upcoming": "upcoming",
	"Expired": "expired",
	"Closed": "expired",
	"Terminated": "expired",
}

DEPOSIT_STATUS = {
	"Received": "received",
	"Received in part": "partly_received",
	"Return in part": "returned",
	"Returned": "returned",
	"Recovered for rent": "returned",
	"Recovered for repairs": "returned",
	"Proforma Invoice raised": "requested",
}

# ERPNext's Issue statuses, and the ones PropMS replaces them with (property setter).
ISSUE_STATUS = {
	"Open": "open",
	"Replied": "in_progress",
	"In Progress": "in_progress",
	"In Discussion": "in_progress",
	"Under Observation": "in_progress",
	"Appointment": "in_progress",
	"On Hold": "on_hold",
	"Hold": "on_hold",
	"Awaiting Parts": "on_hold",
	"Resolved": "resolved",
	"Closed": "closed",
}

# App category → Issue Type created by install.py. Staff see the French name in the desk.
ISSUE_CATEGORIES = {
	"plumbing": "Plomberie",
	"electricity": "Électricité",
	"locksmith": "Serrurerie",
	"painting": "Peinture",
	"air_conditioning": "Climatisation",
	"other": "Autre",
}
APPROVAL_STATUS = {
	"Awaiting approval": "awaiting_approval",
	"In progress": "in_progress",
	"Rejected": "rejected",
	"Completed": "completed",
}
ISSUE_TYPE_TO_CATEGORY = {value: key for key, value in ISSUE_CATEGORIES.items()}


def iso(value) -> str | None:
	return str(getdate(value)) if value else None


def frequency_of(code: str | None) -> tuple[str, int]:
	return FREQUENCIES.get(code or "", ("monthly", 1))


# --------------------------------------------------------------------------- #
# Properties                                                                   #
# --------------------------------------------------------------------------- #

PROPERTY_FIELDS = [
	"name",
	"parent_property",
	"is_group",
	"unit_owner",
	"status",
	"type",
	"bedroom",
	"master_bedroom",
	"common_bathroom",
	"builtup_area",
	"no_of_parking",
	"smoking",
	"furnished",
	"description",
	"rent",
	"lft",
	"rgt",
]


def amenities(property_name: str) -> list[str]:
	"""Amenities listed on a unit in the desk (Property Amenity rows), in their desk order."""
	return [
		row.amenity_name
		for row in frappe.get_all(
			"Property Amenity",
			filters={"parent": property_name, "parenttype": "Property"},
			fields=["amenity_name"],
			order_by="idx asc",
			ignore_permissions=True,
		)
		if row.amenity_name
	]


def get_properties(names) -> dict[str, frappe._dict]:
	if not names:
		return {}
	rows = frappe.get_all(
		"Property",
		filters={"name": ["in", list(names)]},
		fields=PROPERTY_FIELDS,
		order_by="lft asc",
		ignore_permissions=True,
	)
	return {row.name: row for row in rows}


def property_ref(prop: frappe._dict) -> dict:
	parent = prop.parent_property
	return {
		"id": prop.name,
		"name": prop.name,
		"displayName": f"{parent} · {prop.name}" if parent else prop.name,
	}


def ref_for(name: str, cache: dict) -> dict:
	"""Reference for a property name, loading it once when the caller has not."""
	if name not in cache:
		cache.update(get_properties([name]))
	prop = cache.get(name)
	return property_ref(prop) if prop else {"id": name, "name": name, "displayName": name}


def customer_names(names) -> dict[str, str]:
	names = [name for name in set(names) if name]
	if not names:
		return {}
	return {
		row.name: row.customer_name or row.name
		for row in frappe.get_all(
			"Customer",
			filters={"name": ["in", names]},
			fields=["name", "customer_name"],
			ignore_permissions=True,
		)
	}


# --------------------------------------------------------------------------- #
# Leases                                                                       #
# --------------------------------------------------------------------------- #

LEASE_FIELDS = [
	"name",
	"property",
	"customer",
	"lease_customer",
	"start_date",
	"end_date",
	"frequency",
	"lease_status",
	"security_deposit",
	"security_status",
	"notice_period",
	"company",
]


def get_leases(names=None, filters=None) -> list[frappe._dict]:
	if names is not None and not names:
		return []
	query_filters = dict(filters or {})
	if names is not None:
		query_filters["name"] = ["in", list(names)]
	return frappe.get_all(
		"Lease",
		filters=query_filters,
		fields=LEASE_FIELDS,
		order_by="start_date desc",
		ignore_permissions=True,
	)


def lease_status(lease: frappe._dict, on: date) -> str:
	status = LEASE_STATUS.get(lease.lease_status or "")
	if status:
		return status
	start, end = getdate(lease.start_date), getdate(lease.end_date) if lease.end_date else None
	if start and start > on:
		return "upcoming"
	if end and end < on:
		return "expired"
	return "active"


def is_current(lease: frappe._dict, on: date) -> bool:
	"""Running today: not ended, not cancelled, already started."""
	if lease_status(lease, on) not in ("active", "notice_given"):
		return False
	start = getdate(lease.start_date) if lease.start_date else None
	end = getdate(lease.end_date) if lease.end_date else None
	return (not start or start <= on) and (not end or end >= on)


def current_lease_by_property(leases: list[frappe._dict], on: date) -> dict[str, frappe._dict]:
	current: dict[str, frappe._dict] = {}
	for lease in leases:  # newest first
		if lease.property and lease.property not in current and is_current(lease, on):
			current[lease.property] = lease
	return current


def lease_items(lease_names) -> dict[str, list[frappe._dict]]:
	"""Billing lines in force today, per lease: one per item, the latest valid_from wins."""
	if not lease_names:
		return {}
	rows = frappe.get_all(
		"Lease Item",
		filters={"parent": ["in", list(lease_names)], "parenttype": "Lease"},
		fields=["parent", "lease_item", "amount", "frequency", "valid_from", "is_active", "idx"],
		order_by="idx asc",
		ignore_permissions=True,
	)
	on = getdate(today())
	chosen: dict[tuple[str, str], frappe._dict] = {}
	for row in rows:
		if row.valid_from and getdate(row.valid_from) > on:
			continue
		key = (row.parent, row.lease_item)
		best = chosen.get(key)
		if best is None or getdate(row.valid_from or "1900-01-01") >= getdate(
			best.valid_from or "1900-01-01"
		):
			chosen[key] = row
	per_lease: dict[str, list[frappe._dict]] = defaultdict(list)
	for (parent, _item), row in chosen.items():
		per_lease[parent].append(row)
	return per_lease


def item_names(codes) -> dict[str, str]:
	codes = [code for code in set(codes) if code]
	if not codes:
		return {}
	return {
		row.name: row.item_name or row.name
		for row in frappe.get_all(
			"Item", filters={"name": ["in", codes]}, fields=["name", "item_name"], ignore_permissions=True
		)
	}


def amount_per_period(lease: frappe._dict, items: list[frappe._dict]) -> float:
	"""Lease Item amounts are monthly in PropMS; one period covers ``months`` of them."""
	_key, months = frequency_of(lease.frequency)
	return sum(flt(item.amount) for item in items) * months


def lease_summary(
	lease: frappe._dict, items: list[frappe._dict], tenants: dict, props: dict, on: date
) -> dict:
	key, _months = frequency_of(lease.frequency)
	return {
		"id": lease.name,
		"status": lease_status(lease, on),
		"tenant": {"id": lease.customer, "name": tenants.get(lease.customer, lease.customer)},
		"property": ref_for(lease.property, props),
		"startDate": iso(lease.start_date),
		"endDate": iso(lease.end_date),
		"frequency": key,
		"amountPerPeriod": amount_per_period(lease, items),
	}


def lease_summaries(leases: list[frappe._dict], props: dict, on: date) -> list[dict]:
	items = lease_items([lease.name for lease in leases])
	tenants = customer_names([lease.customer for lease in leases])
	return [lease_summary(lease, items.get(lease.name, []), tenants, props, on) for lease in leases]


def deposit(lease: frappe._dict) -> dict | None:
	if not flt(lease.security_deposit):
		return None
	return {
		"amount": flt(lease.security_deposit),
		"status": DEPOSIT_STATUS.get(lease.security_status or "", "unknown"),
	}


def schedule_lines(
	lease: frappe._dict, items: list[frappe._dict], invoices: dict[str, dict], on: date
) -> list[dict]:
	"""Rent schedule: PropMS schedule rows, then the periods still to come until the lease ends.

	PropMS only writes schedule rows up to next month. The tenant wants to see
	the whole lease, so later periods are projected from the lease items and
	shown as "upcoming"; they have no invoice yet.
	"""
	_key, months = frequency_of(lease.frequency)
	end = getdate(lease.end_date) if lease.end_date else None

	rows = frappe.get_all(
		"Lease Invoice Schedule",
		filters={"parent": lease.name, "parenttype": "Lease"},
		fields=["name", "schedule_start_date", "date_to_invoice", "qty", "rate", "invoice_number"],
		order_by="schedule_start_date asc, idx asc",
		ignore_permissions=True,
	)
	periods: dict[date, dict] = {}
	for row in rows:
		start = getdate(row.schedule_start_date or row.date_to_invoice)
		if not start:
			continue
		line = periods.setdefault(start, {"start": start, "amount": 0.0, "invoices": [], "id": row.name})
		line["amount"] += flt(row.qty) * flt(row.rate)
		if row.invoice_number and row.invoice_number not in line["invoices"]:
			line["invoices"].append(row.invoice_number)

	# Projected periods, aligned like PropMS: first day of the month, one step per period.
	per_period = amount_per_period(lease, items)
	if lease.start_date and per_period:
		cursor = get_first_day(lease.start_date)
		this_month = get_first_day(on)
		guard = 0
		while (end is None or cursor <= end) and guard < 240:
			if cursor >= this_month and cursor not in periods:
				periods[cursor] = {
					"start": cursor,
					"amount": per_period,
					"invoices": [],
					"id": f"{lease.name}:{cursor}",
				}
			if end is None and cursor > add_months(on, 12):
				break
			cursor = getdate(add_months(cursor, months))
			guard += 1

	lines = []
	for start in sorted(periods):
		line = periods[start]
		period_end = getdate(get_last_day(add_months(start, months - 1)))
		if end and period_end > end:
			period_end = end
		linked = [invoices[name] for name in line["invoices"] if name in invoices]
		if line["invoices"] and not linked:
			# Invoiced, but not to this user (another payer): neither theirs nor "upcoming".
			continue
		if linked:
			outstanding = sum(invoice["outstanding"] for invoice in linked)
			amount = sum(invoice["total"] for invoice in linked)
			due = min(invoice["dueDate"] for invoice in linked)
			statuses = {invoice["status"] for invoice in linked}
			status = (
				"paid"
				if outstanding <= 0
				else "overdue"
				if "overdue" in statuses
				else "partly_paid"
				if "partly_paid" in statuses
				else "due"
			)
		else:
			outstanding, amount, due = line["amount"], line["amount"], iso(start)
			status = "upcoming"
		lines.append(
			{
				"id": line["id"],
				"periodStart": iso(start),
				"periodEnd": iso(period_end),
				"dueDate": due,
				"amount": amount,
				"outstanding": outstanding,
				"status": status,
				"invoiceId": linked[0]["id"] if linked else None,
			}
		)
	return lines


# --------------------------------------------------------------------------- #
# Invoices and payments                                                        #
# --------------------------------------------------------------------------- #

INVOICE_FIELDS = [
	"name",
	"customer",
	"customer_name",
	"lease",
	"posting_date",
	"due_date",
	"from_date",
	"to_date",
	"grand_total",
	"outstanding_amount",
	"currency",
]


def invoice_status(total: float, outstanding: float, due: date | None, on: date) -> str:
	if outstanding <= 0:
		return "paid"
	if due and due < on:
		return "overdue"
	if outstanding < total:
		return "partly_paid"
	return "due"


def invoice_summaries(filters: dict, lease_property: dict[str, str], props: dict, on: date) -> list[dict]:
	rows = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=INVOICE_FIELDS,
		order_by="due_date desc, name desc",
		ignore_permissions=True,
	)
	missing = {lease_property.get(row.lease) for row in rows} - set(props) - {None}
	if missing:
		props.update(get_properties(missing))
	result = []
	for row in rows:
		total, outstanding = flt(row.grand_total), flt(row.outstanding_amount)
		due = getdate(row.due_date) if row.due_date else None
		status = invoice_status(total, outstanding, due, on)
		prop = lease_property.get(row.lease)
		result.append(
			{
				"id": row.name,
				"status": status,
				"tenant": {"id": row.customer, "name": row.customer_name or row.customer},
				"property": ref_for(prop, props) if prop else None,
				"leaseId": row.lease,
				"postingDate": iso(row.posting_date),
				"dueDate": iso(row.due_date or row.posting_date),
				"periodStart": iso(row.from_date or row.posting_date),
				"periodEnd": iso(row.to_date or row.from_date or row.posting_date),
				"total": total,
				"outstanding": outstanding,
				"daysLate": date_diff(on, due) if status == "overdue" else 0,
			}
		)
	return result


def payments_for(invoice_names, since=None, until=None) -> list[dict]:
	"""Submitted Payment Entries allocated to these invoices, newest first; dated ``since``..``until``."""
	if not invoice_names:
		return []
	pe = DocType("Payment Entry")
	ref = DocType("Payment Entry Reference")
	rows = (
		frappe.qb.from_(ref)
		.join(pe)
		.on(ref.parent == pe.name)
		.select(
			pe.name,
			pe.posting_date,
			pe.mode_of_payment,
			pe.reference_no,
			pe.party_name,
			ref.reference_name,
			ref.allocated_amount,
		)
		.where(pe.docstatus == 1)
		.where(ref.parenttype == "Payment Entry")
		.where(ref.reference_doctype == "Sales Invoice")
		.where(ref.reference_name.isin(list(invoice_names)))
		.where(pe.posting_date >= since if since else pe.docstatus == 1)
		.where(pe.posting_date <= until if until else pe.docstatus == 1)
		.orderby(pe.posting_date, order=frappe.qb.desc)
		.orderby(pe.name, order=frappe.qb.desc)
	).run(as_dict=True)
	return [
		{
			"id": row.name,
			"invoiceId": row.reference_name,
			"date": iso(row.posting_date),
			"amount": flt(row.allocated_amount),
			"mode": row.mode_of_payment,
			"reference": row.reference_no,
			"payerName": row.party_name,
		}
		for row in rows
	]


def invoice_items(invoice_name: str) -> list[dict]:
	rows = frappe.get_all(
		"Sales Invoice Item",
		filters={"parent": invoice_name, "parenttype": "Sales Invoice"},
		fields=["item_name", "item_code", "amount", "idx"],
		order_by="idx asc",
		ignore_permissions=True,
	)
	return [{"label": row.item_name or row.item_code, "amount": flt(row.amount)} for row in rows]


# --------------------------------------------------------------------------- #
# Maintenance                                                                  #
# --------------------------------------------------------------------------- #

ISSUE_FIELDS = [
	"name",
	"subject",
	"status",
	"issue_type",
	"priority",
	"opening_date",
	"opening_time",
	"creation",
	"property_name",
	"customer",
	"customer_name",
	"sky_immo_status",
]


def issue_summary(row: frappe._dict, props: dict) -> dict:
	created = (
		f"{row.opening_date}T{str(row.opening_time or '00:00:00')[:8]}"
		if row.opening_date
		else str(row.creation)
	)
	return {
		"id": row.name,
		"title": row.subject,
		"category": ISSUE_TYPE_TO_CATEGORY.get(row.issue_type or "", "other"),
		"urgent": (row.priority or "") in ("High", "Urgent"),
		"status": ISSUE_STATUS.get(row.status or "", "open"),
		# Owner decision: awaiting_approval, in_progress, rejected or completed.
		"approval": APPROVAL_STATUS.get(row.get("sky_immo_status") or "", "awaiting_approval"),
		"createdAt": created.replace(" ", "T"),
		"property": ref_for(row.property_name, props) if row.property_name else None,
		"tenantName": row.customer_name or row.customer,
	}
