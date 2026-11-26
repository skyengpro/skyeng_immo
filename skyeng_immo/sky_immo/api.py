"""Endpoints of the Sky Immo app, called from the Vue frontend.

Each one reads the signed-in user's scope first (:func:`skyeng_immo.access.get_scope`, the one
computation of what a user may see) and only ever returns records inside it. Landlords and tenants have no other access
to PropMS or ERPNext data. The only write a landlord or tenant can make is
the tenant's maintenance request, plus their own language preference.
"""

import base64
import binascii
import html
import io
import json
import re

import frappe
from frappe import _
from frappe.utils import (
	add_days,
	add_to_date,
	escape_html,
	flt,
	get_first_day,
	getdate,
	now_datetime,
	strip_html,
	today,
)
from PIL import Image

from skyeng_immo import access
from skyeng_immo.access import Scope

from . import data, maintenance

LANGUAGES = ("fr", "en")
MAX_PHOTOS = 2
MAX_PHOTO_BYTES = 5 * 1024 * 1024
MAX_ISSUES_PER_HOUR = 10
# Types a photo may declare in its data URL; its content is then checked (`_image_extension`).
PHOTO_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
# Pillow's name of each accepted format, and the file extension the photo is saved with.
PHOTO_FORMATS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


def _scope(side: str | None = None) -> Scope:
	"""Scope of the signed-in user; 403 without an app role, or without the role `side` needs.

	`side` "owner" (Landlord or manager) narrows the scope to the properties the user owns or
	manages, "tenant" (Tenant) to the user's own leases. None keeps every role the user holds.
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	allowed = access.app_space(user) is not None and (
		side is None
		or (side == "owner" and (access.is_manager(user) or access.LANDLORD in roles))
		or (side == "tenant" and access.TENANT in roles)
	)
	if not allowed:
		frappe.throw(_("You do not have access to this page."), frappe.PermissionError)
	scope = access.get_scope(user)
	if side == "owner":
		return access.owner_side(scope)
	if side == "tenant":
		return access.tenant_side(scope)
	return scope


def _not_found():
	"""Same answer for 'does not exist' and 'not yours', so names cannot be probed."""
	frappe.throw(_("Not found"), frappe.DoesNotExistError)


def _invoice_filters(scope: Scope) -> dict:
	"""Rent invoices of the scope (credit notes are not listed)."""
	return {**access.invoice_filters(scope), "is_return": 0}


def _can_see_invoice(scope: Scope, name: str) -> bool:
	return bool(name and scope.leases) and bool(
		frappe.db.exists("Sales Invoice", {**_invoice_filters(scope), "name": name})
	)


def _default_currency() -> str:
	company = frappe.defaults.get_global_default("company")
	currency = company and frappe.get_cached_value("Company", company, "default_currency")
	return currency or frappe.defaults.get_global_default("currency") or "XAF"


# --------------------------------------------------------------------------- #
# Session                                                                      #
# --------------------------------------------------------------------------- #


@frappe.whitelist(methods=["GET"])
def get_session() -> dict:
	"""Who is signed in, their app space, and the CSRF token for later POSTs."""
	user = frappe.session.user
	result = {"user": None, "noAccess": False, "currency": _default_currency(), "csrfToken": None}
	if user == "Guest":
		return result

	result["csrfToken"] = frappe.sessions.get_csrf_token()
	role = access.app_space(user)
	if role is None:
		# Signed in, but neither staff, landlord nor tenant (e.g. a supplier portal user).
		result["noAccess"] = True
		return result

	info = frappe.db.get_value("User", user, ["first_name", "full_name", "email", "language"], as_dict=True)
	language = (info.language or "")[:2]
	result["user"] = {
		"id": user,
		"role": role,
		"firstName": info.first_name or info.full_name or user,
		"fullName": info.full_name or user,
		"email": info.email or user,
		"language": language if language in LANGUAGES else None,
	}
	return result


@frappe.whitelist(methods=["POST"])
def set_language(lang: str) -> None:
	"""Saved on the User so that emails also go out in this language."""
	if lang not in LANGUAGES:
		frappe.throw(_("Unsupported language"))
	_scope()
	frappe.db.set_value("User", frappe.session.user, "language", lang)
	frappe.clear_cache(user=frappe.session.user)


# --------------------------------------------------------------------------- #
# Landlord and property manager                                                #
# --------------------------------------------------------------------------- #


def _context(scope: Scope):
	"""Properties and leases of the scope, loaded once per request."""
	props = data.get_properties(scope.properties)
	leases = data.get_leases(scope.leases)
	lease_property = {lease.name: lease.property for lease in leases}
	return props, leases, lease_property


@frappe.whitelist(methods=["GET"])
def get_owner_dashboard() -> dict:
	scope = _scope("owner")
	on = getdate(today())
	props, leases, lease_property = _context(scope)
	current = [lease for lease in leases if data.is_current(lease, on)]

	unpaid = data.invoice_summaries(
		{**_invoice_filters(scope), "outstanding_amount": [">", 0]}, lease_property, props, on
	)
	overdue = sorted((inv for inv in unpaid if inv["status"] == "overdue"), key=lambda inv: -inv["daysLate"])

	invoice_names = frappe.get_all("Sales Invoice", filters=_invoice_filters(scope), pluck="name")
	collected = sum(
		payment["amount"] for payment in data.payments_for(invoice_names, since=get_first_day(on))
	)

	first_name = frappe.db.get_value("User", scope.user, "first_name") or ""
	return {
		"firstName": first_name,
		"stats": {
			"properties": sum(1 for prop in props.values() if not prop.is_group),
			"tenants": len({lease.customer for lease in current if lease.customer}),
			"collectedThisMonth": collected,
			"unpaidTotal": sum(inv["outstanding"] for inv in unpaid),
			"unpaidCount": len(unpaid),
		},
		"overdue": overdue,
	}


def _property_summary(prop, current_lease, items, tenants, on) -> dict:
	if prop.status == "In Renovation":
		status = "renovation"
	elif current_lease:
		end = getdate(current_lease.end_date) if current_lease.end_date else None
		ending = end and (end - on).days <= data.ENDING_SOON_DAYS
		status = "ending_soon" if ending or current_lease.lease_status == "Vacating" else "let"
	else:
		status = "available"

	if current_lease:
		key, _months = data.frequency_of(current_lease.frequency)
		rent = {"amount": data.amount_per_period(current_lease, items), "frequency": key}
	else:
		rent = {"amount": flt(prop.rent), "frequency": "monthly"}

	return {
		**data.property_ref(prop),
		"type": prop.type,
		"status": status,
		"tenantName": tenants.get(current_lease.customer, current_lease.customer) if current_lease else None,
		"rent": rent,
	}


@frappe.whitelist(methods=["GET"])
def list_properties() -> dict:
	"""Units of the scope, grouped by building; for staff, by landlord first."""
	scope = _scope("owner")
	on = getdate(today())
	props, leases, _lease_property = _context(scope)
	current = data.current_lease_by_property(leases, on)
	items = data.lease_items([lease.name for lease in current.values()])
	tenants = data.customer_names([lease.customer for lease in current.values()])

	def owner_of(prop):
		while prop is not None:
			if prop.unit_owner:
				return prop.unit_owner
			prop = props.get(prop.parent_property)
		return None

	units = [prop for prop in props.values() if not prop.is_group]
	owners = data.customer_names(owner_of(unit) for unit in units)
	by_landlord = access.is_manager(scope.user) and len({owner_of(unit) for unit in units}) > 1

	sections: dict = {}
	for unit in units:  # ordered by tree position
		landlord_key = owner_of(unit) if by_landlord else None
		section = sections.setdefault(
			landlord_key,
			{
				"landlord": {"id": landlord_key, "name": owners.get(landlord_key, landlord_key)}
				if landlord_key
				else None,
				"groups": {},
			},
		)
		building = props.get(unit.parent_property) if unit.parent_property else None
		group = section["groups"].setdefault(
			building.name if building else None,
			{"building": {"id": building.name, "name": building.name} if building else None, "units": []},
		)
		lease = current.get(unit.name)
		group["units"].append(
			_property_summary(unit, lease, items.get(lease.name, []) if lease else [], tenants, on)
		)

	result = []
	for key in sorted(sections, key=lambda value: (value is None, (owners.get(value) or "").lower())):
		section = sections[key]
		groups = sorted(section["groups"].values(), key=lambda group: group["building"] is None)
		result.append({"landlord": section["landlord"], "groups": groups})
	return {"byLandlord": by_landlord, "sections": result}


@frappe.whitelist(methods=["GET"])
def get_property(name: str) -> dict:
	scope = _scope("owner")
	if name not in scope.properties:
		_not_found()
	on = getdate(today())
	props = data.get_properties([name])
	prop = props[name]
	if prop.parent_property:
		props.update(data.get_properties([prop.parent_property]))

	visible = set(scope.leases)
	leases = [lease for lease in data.get_leases(filters={"property": name}) if lease.name in visible]
	current = data.current_lease_by_property(leases, on).get(name)
	items = data.lease_items([lease.name for lease in leases])
	tenants = data.customer_names([lease.customer for lease in leases])
	lease_property = {lease.name: lease.property for lease in leases}

	invoices = (
		data.invoice_summaries(
			{**_invoice_filters(scope), "lease": ["in", list(lease_property)]}, lease_property, props, on
		)
		if lease_property
		else []
	)
	by_id = {invoice["id"]: invoice for invoice in invoices}

	current_detail = None
	if current:
		current_items = items.get(current.name, [])
		current_detail = {
			**data.lease_summary(current, current_items, tenants, props, on),
			"deposit": data.deposit(current),
			"schedule": data.schedule_lines(current, current_items, by_id, on),
		}

	return {
		**_property_summary(prop, current, items.get(current.name, []) if current else [], tenants, on),
		"buildingName": prop.parent_property,
		"isBuilding": bool(prop.is_group),
		"features": {
			"type": prop.type,
			"bedrooms": prop.bedroom or 0,
			"bathrooms": prop.common_bathroom or 0,
			"area": flt(prop.builtup_area),
			"furnished": bool(prop.furnished),
		},
		"currentLease": current_detail,
		"invoices": invoices,
		"pastLeases": [
			data.lease_summary(lease, items.get(lease.name, []), tenants, props, on)
			for lease in leases
			if not current or lease.name != current.name
		],
	}


# --------------------------------------------------------------------------- #
# Leases (landlord "tenant" screen, tenant "my lease" screen)                  #
# --------------------------------------------------------------------------- #


@frappe.whitelist(methods=["GET"])
def get_lease(name: str) -> dict:
	scope = _scope()
	if name not in scope.leases:
		_not_found()
	on = getdate(today())
	lease = data.get_leases([name])[0]
	props = data.get_properties([lease.property]) if lease.property else {}
	prop = props.get(lease.property)
	if prop and prop.parent_property:
		props.update(data.get_properties([prop.parent_property]))

	items = data.lease_items([name]).get(name, [])
	tenants = data.customer_names([lease.customer])
	invoices = data.invoice_summaries(
		{**_invoice_filters(scope), "lease": name}, {name: lease.property}, props, on
	)
	by_id = {invoice["id"]: invoice for invoice in invoices}
	_key, months = data.frequency_of(lease.frequency)
	labels = data.item_names(item.lease_item for item in items)

	tenant_contact = {}
	# Contact details for the landlord or manager of the property, not for the tenant themselves.
	if name in scope.owned_leases and lease.customer:
		tenant_contact = (
			frappe.db.get_value("Customer", lease.customer, ["email_id", "mobile_no"], as_dict=True) or {}
		)

	return {
		**data.lease_summary(lease, items, tenants, props, on),
		"tenantEmail": tenant_contact.get("email_id"),
		"tenantPhone": tenant_contact.get("mobile_no"),
		"noticeDays": lease.notice_period or 0,
		"deposit": data.deposit(lease),
		"lines": [
			{"label": labels.get(item.lease_item, item.lease_item), "amount": flt(item.amount) * months}
			for item in items
		],
		"schedule": data.schedule_lines(lease, items, by_id, on),
		"invoicesDue": [invoice for invoice in invoices if invoice["outstanding"] > 0],
		"payments": data.payments_for(list(by_id)),
	}


# --------------------------------------------------------------------------- #
# Invoices                                                                     #
# --------------------------------------------------------------------------- #


def _all_lease_properties(scope: Scope) -> dict[str, str]:
	return {lease.name: lease.property for lease in data.get_leases(scope.leases)}


@frappe.whitelist(methods=["GET"])
def list_invoices(tab: str = "unpaid") -> list[dict]:
	scope = _scope()
	filters = _invoice_filters(scope)
	filters["outstanding_amount"] = [">", 0] if tab == "unpaid" else ["<=", 0]
	return data.invoice_summaries(filters, _all_lease_properties(scope), {}, getdate(today()))


@frappe.whitelist(methods=["GET"])
def get_invoice(name: str) -> dict:
	scope = _scope()
	if not _can_see_invoice(scope, name):
		_not_found()
	summary = data.invoice_summaries(
		{**_invoice_filters(scope), "name": name}, _all_lease_properties(scope), {}, getdate(today())
	)[0]
	return {**summary, "items": data.invoice_items(name), "payments": data.payments_for([name])}


@frappe.whitelist(methods=["GET"])
def download(kind: str, name: str):
	"""PDF of an invoice or of a receipt (the Payment Entry), from the standard print format."""
	scope = _scope()
	if kind == "invoice":
		if not _can_see_invoice(scope, name):
			_not_found()
		doctype = "Sales Invoice"
	elif kind == "receipt":
		invoices = frappe.get_all(
			"Payment Entry Reference",
			filters={"parent": name, "parenttype": "Payment Entry", "reference_doctype": "Sales Invoice"},
			pluck="reference_name",
			ignore_permissions=True,
		)
		# Only a receipt entirely about the user's own invoices: one payment can settle the rent
		# of two landlords, or of two leases with different tenants.
		allowed = bool(invoices) and all(_can_see_invoice(scope, invoice) for invoice in invoices)
		if not allowed or frappe.db.get_value("Payment Entry", name, "docstatus") != 1:
			_not_found()
		doctype = "Payment Entry"
	else:
		_not_found()

	from frappe.translate import print_language

	language = (frappe.db.get_value("User", scope.user, "language") or "fr")[:2]
	previous = frappe.flags.ignore_print_permissions
	frappe.flags.ignore_print_permissions = True
	try:
		with print_language(language):
			try:
				pdf = frappe.get_print(doctype, name, as_pdf=True)
			except Exception:
				# PDF engine down or misconfigured (wkhtmltopdf cannot reach the site):
				# the person still gets their document, as a printable page.
				frappe.clear_last_message()
				frappe.log_error(f"Sky Immo: PDF of {doctype} {name}, falling back to HTML")
				from werkzeug.wrappers import Response

				page = frappe.get_print(doctype, name)
				return Response(page, mimetype="text/html")
	finally:
		frappe.flags.ignore_print_permissions = previous

	frappe.local.response.filename = "{}.pdf".format(re.sub(r"[^\w.-]+", "-", name))
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"


# --------------------------------------------------------------------------- #
# Tenant                                                                       #
# --------------------------------------------------------------------------- #


def _issues(scope: Scope, limit: int | None = None) -> list[dict]:
	"""Requests in scope, newest first: all of an owned property's, a tenant's own on their units."""
	props: dict = {}
	return [
		data.issue_summary(row, props) for row in access.get_issues(scope, data.ISSUE_FIELDS, limit=limit)
	]


@frappe.whitelist(methods=["GET"])
def get_tenant_home() -> dict:
	scope = _scope("tenant")
	on = getdate(today())
	props, leases, lease_property = _context(scope)
	current = [lease for lease in leases if data.is_current(lease, on)]
	unpaid = sorted(
		data.invoice_summaries(
			{**_invoice_filters(scope), "outstanding_amount": [">", 0]}, lease_property, props, on
		),
		key=lambda invoice: invoice["dueDate"],
	)

	next_due = None
	if unpaid:
		# `unpaid` is sorted by due date: the first one is the oldest unpaid invoice.
		next_due = {"kind": "invoice", "invoice": unpaid[0]}
	elif current:
		# Nothing to pay: the next period not invoiced yet, read against the real invoices.
		items = data.lease_items([lease.name for lease in current])
		invoiced = {
			invoice["id"]: invoice
			for invoice in data.invoice_summaries(
				{**_invoice_filters(scope), "lease": ["in", [lease.name for lease in current]]},
				lease_property,
				props,
				on,
			)
		}
		upcoming = []
		for lease in current:
			for line in data.schedule_lines(lease, items.get(lease.name, []), invoiced, on):
				if line["status"] == "upcoming" and line["dueDate"] >= str(add_days(on, -31)):
					upcoming.append(line)
					break
		if upcoming:
			next_due = {"kind": "schedule", "line": min(upcoming, key=lambda line: line["dueDate"])}

	first_name = frappe.db.get_value("User", scope.user, "first_name") or ""
	latest = _issues(scope, limit=1)
	return {
		"firstName": first_name,
		"next": next_due,
		"balanceDue": sum(invoice["outstanding"] for invoice in unpaid),
		"unpaidCount": len(unpaid),
		"homes": [
			{
				"leaseId": lease.name,
				"property": data.ref_for(lease.property, props),
				"endDate": data.iso(lease.end_date),
			}
			for lease in current
		],
		"latestIssue": latest[0] if latest else None,
	}


@frappe.whitelist(methods=["GET"])
def list_my_leases() -> list[dict]:
	"""Tenant's leases, current first, for the "My lease" screen."""
	scope = _scope("tenant")
	on = getdate(today())
	props, leases, _lease_property = _context(scope)
	summaries = data.lease_summaries(leases, props, on)
	return sorted(summaries, key=lambda lease: lease["status"] not in ("active", "notice_given"))


# --------------------------------------------------------------------------- #
# Maintenance                                                                  #
# --------------------------------------------------------------------------- #


@frappe.whitelist(methods=["GET"])
def list_issues() -> list[dict]:
	"""Tenant: own requests. Landlord and manager: requests on their properties."""
	return _issues(_scope())


@frappe.whitelist(methods=["GET"])
def get_issue(name: str) -> dict:
	scope = _scope()
	rows = access.get_issues(
		scope, [*data.ISSUE_FIELDS, "description", "resolution_details", "attachment"], name=name
	)
	if not rows:
		_not_found()
	row = frappe._dict(rows[0])
	# The landlord's name is for the owner side; a tenant does not see who owns the unit.
	owner_view = row.property_name in scope.owned_properties
	owner = maintenance.effective_owner(row.property_name) if owner_view else None

	replies = frappe.get_all(
		"Communication",
		filters={
			"reference_doctype": "Issue",
			"reference_name": name,
			"communication_type": "Communication",
			"sent_or_received": "Sent",
		},
		fields=["sender_full_name", "sender", "content", "communication_date"],
		order_by="communication_date asc",
		ignore_permissions=True,
	)
	return {
		**data.issue_summary(row, {}),
		"description": html.unescape(strip_html(row.description or "")).strip(),
		"resolution": html.unescape(strip_html(row.resolution_details or "")).strip() or None,
		"photos": _issue_photos(name),
		"hasPhoto": bool(row.attachment),
		"canDecide": maintenance.can_decide(name, scope.user),
		"canComplete": maintenance.can_complete(name, scope.user),
		"landlordName": frappe.db.get_value("Customer", owner, "customer_name") if owner else None,
		"replies": [
			{
				"author": reply.sender_full_name or reply.sender,
				"message": html.unescape(strip_html(reply.content or "")).strip(),
				"at": str(reply.communication_date).replace(" ", "T"),
			}
			for reply in replies
		],
	}


def _issue_photos(name: str) -> list[dict]:
	"""Private files attached to a request, oldest first: the app opens them through `issue_photo`."""
	return [
		{"id": f.name, "name": f.file_name}
		for f in frappe.get_all(
			"File",
			filters={"attached_to_doctype": "Issue", "attached_to_name": name, "is_private": 1},
			fields=["name", "file_name"],
			order_by="creation asc",
			ignore_permissions=True,
		)
	]


@frappe.whitelist(methods=["GET"])
def issue_photo(name: str, file: str | None = None):
	"""A photo of a request, only for a user who can see that request (403 otherwise).

	Frappe serves a private file to users who can read the Issue; landlords and tenants cannot,
	so this method checks the scope, then returns the file.
	"""
	if not access.get_issues(_scope(), ["name"], name=name):
		frappe.throw(_("You do not have access to this photo."), frappe.PermissionError)
	photos = _issue_photos(name)
	chosen = next((p for p in photos if p["id"] == file), None) if file else (photos[0] if photos else None)
	if not chosen:
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	doc = frappe.get_doc("File", chosen["id"])
	try:
		content = doc.get_content()
	except (OSError, frappe.DoesNotExistError):
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	if isinstance(content, str):
		content = content.encode()
	extension = (doc.file_name or "").rsplit(".", 1)[-1].lower()
	frappe.local.response.filename = doc.file_name or f"{name}.jpg"
	frappe.local.response.filecontent = content
	frappe.local.response.type = "download"
	frappe.local.response.display_content_as = "inline"
	frappe.local.response["content_type"] = {"png": "image/png", "webp": "image/webp"}.get(
		extension, "image/jpeg"
	)


@frappe.whitelist(methods=["POST"])
def decide_issue(name: str, decision: str) -> dict:
	"""Landlord approves or rejects a request awaiting approval (the app's button)."""
	_scope("owner")
	return maintenance.decide(name, decision)


@frappe.whitelist(methods=["POST"])
def complete_issue(name: str) -> dict:
	"""The tenant who made a request closes it, once the work is done."""
	_scope("tenant")
	return maintenance.complete(name)


def _decode_photo(photo: str, position: int = 1) -> tuple[bytes, str]:
	"""One photo sent as a data URL. Images only, 5 MB at most, with a message the tenant can act on."""
	match = re.match(r"^data:(image/[a-z+.-]+);base64,(.+)$", photo or "", re.DOTALL)
	if not match or match.group(1) not in PHOTO_TYPES:
		frappe.throw(
			_("Photo {0} is not an image. Only JPEG, PNG or WebP photos are accepted.").format(position),
			title=_("Photo refused"),
		)
	too_large = _("Photo {0} is larger than {1} MB. Please choose a smaller one.").format(
		position, MAX_PHOTO_BYTES // (1024 * 1024)
	)
	# Base64 is 4 characters per 3 bytes: refuse an oversized photo before decoding it.
	if len(match.group(2)) > (MAX_PHOTO_BYTES + 2) // 3 * 4 + 4:
		frappe.throw(too_large, title=_("Photo refused"))
	try:
		content = base64.b64decode(match.group(2), validate=True)
	except (binascii.Error, ValueError):
		frappe.throw(
			_("Photo {0} could not be read. Please choose another one.").format(position),
			title=_("Photo refused"),
		)
	if len(content) > MAX_PHOTO_BYTES:
		frappe.throw(too_large, title=_("Photo refused"))
	extension = _image_extension(content)
	if not extension:
		frappe.throw(
			_("Photo {0} is not an image. Only JPEG, PNG or WebP photos are accepted.").format(position),
			title=_("Photo refused"),
		)
	return content, extension


def _image_extension(content: bytes) -> str | None:
	"""File extension of a JPEG, PNG or WebP image, read from its content; None for anything else.

	The data URL's type is only what the browser claims: the bytes decide.
	"""
	try:
		with Image.open(io.BytesIO(content)) as image:
			image_format = image.format
			image.verify()
	except Exception:
		# Pillow raises many types on corrupt or hostile input (incl. DecompressionBombError).
		return None
	return PHOTO_FORMATS.get(image_format)


def _photo_list(photos, photo) -> list[str]:
	"""The photos of a request as a list of data URLs; `photo` is the single-photo form of older clients."""
	if isinstance(photos, str):
		try:
			photos = json.loads(photos) if photos.strip() else []
		except ValueError:
			photos = [photos]
	items = [p for p in (photos or []) if p]
	if photo:
		items.append(photo)
	if len(items) > MAX_PHOTOS:
		frappe.throw(_("You can add up to {0} photos.").format(MAX_PHOTOS), title=_("Too many photos"))
	return items


@frappe.whitelist(methods=["POST"])
def create_issue(
	description: str,
	category: str = "other",
	title: str | None = None,
	property: str | None = None,
	urgent: bool | int | str = False,
	photos: list | str | None = None,
	photo: str | None = None,
) -> dict:
	"""A tenant reports a problem in a home they rent. It lands in the desk as an Issue, awaiting approval.

	Only a unit of one of the tenant's active leases is accepted. The description is required;
	up to two photos (images, 5 MB each) are optional. The Issue is inserted with ignore_permissions,
	its customer is then set to the lease's customer with a direct write (ERPNext clears it for
	Website Users), and the photos are saved as private files attached to it (the standard
	`upload_file` needs write permission on the Issue).
	"""
	scope = _scope("tenant")
	# Per account, not per IP: tenants on one mobile network share addresses.
	recent = frappe.db.count(
		"Issue", {"raised_by": scope.user, "creation": [">", add_to_date(now_datetime(), hours=-1)]}
	)
	if recent >= MAX_ISSUES_PER_HOUR:
		frappe.throw(_("Too many requests in one hour. Please call your property manager."))
	description = (description or "").strip()
	if not description:
		frappe.throw(_("Please describe the problem."), title=_("Description missing"))
	title = (title or "").strip() or (description.splitlines()[0])[:80]
	if category not in data.ISSUE_CATEGORIES:
		category = "other"

	on = getdate(today())
	leases = [lease for lease in data.get_leases(scope.leases) if data.is_current(lease, on)]
	if property:
		lease = next((lease for lease in leases if lease.property == property), None)
		if lease is None:
			frappe.throw(
				_("You can only report a problem on a home you currently rent."),
				frappe.PermissionError,
			)
	else:
		lease = leases[0] if len(leases) == 1 else None
		if lease is None:
			frappe.throw(_("Please choose the home concerned."))

	# Every photo is checked before anything is written.
	decoded = [_decode_photo(p, i) for i, p in enumerate(_photo_list(photos, photo), start=1)]

	issue_type = data.ISSUE_CATEGORIES[category]
	urgent = str(urgent).lower() in ("1", "true")
	priority = "High" if urgent else "Medium"
	email = frappe.db.get_value("User", scope.user, "email") or scope.user

	issue = frappe.get_doc(
		{
			"doctype": "Issue",
			"subject": title[:140],
			# Tenant text is escaped: staff read it as HTML in the desk.
			"description": escape_html(description).replace("\n", "<br>"),
			"raised_by": email,
			"property_name": lease.property,
			"company": lease.company,
			"issue_type": issue_type if frappe.db.exists("Issue Type", issue_type) else None,
			"priority": priority if frappe.db.exists("Issue Priority", priority) else None,
			"via_customer_portal": 1,
			"sky_immo_status": maintenance.AWAITING,
		}
	)
	# PropMS makes "person in charge" mandatory; staff set it when they take the request.
	issue.flags.ignore_mandatory = True
	issue.insert(ignore_permissions=True)
	# ERPNext clears Issue.customer for Website Users on save: write it directly.
	frappe.db.set_value("Issue", issue.name, "customer", lease.lease_customer or lease.customer)

	for position, (content, extension) in enumerate(decoded, start=1):
		file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"{issue.name}-photo-{position}.{extension}",
				"attached_to_doctype": "Issue",
				"attached_to_name": issue.name,
				"is_private": 1,
				"content": content,
			}
		)
		file.insert(ignore_permissions=True)
		if position == 1:
			issue.db_set("attachment", file.file_url, update_modified=False)

	return {"id": issue.name}
