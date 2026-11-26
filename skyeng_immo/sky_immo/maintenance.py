"""Maintenance decisions: the owner of a property approves or rejects its tenants' requests.

The decision lives in the Custom Field ``Issue.sky_immo_status`` (fixture). ERPNext resets
``Issue.status`` when a Website User saves an Issue (``restore_staff_only_fields``), so the
decision is written with ``frappe.db.set_value`` and mirrored on ``status`` the same way:
Rejected shows as Closed in the desk, Completed as Resolved.

"Linked to the owner": the user is in the Portal Users of the Customer set as ``unit_owner``
on the property, or on its nearest parent that has one.
"""

import frappe
from frappe import _

from skyeng_immo.access import get_customers

AWAITING = "Awaiting approval"
IN_PROGRESS = "In progress"
REJECTED = "Rejected"
COMPLETED = "Completed"
STATUSES = (AWAITING, IN_PROGRESS, REJECTED, COMPLETED)

# App value for each decision status.
APP_STATUS = {
	AWAITING: "awaiting_approval",
	IN_PROGRESS: "in_progress",
	REJECTED: "rejected",
	COMPLETED: "completed",
}

# What Issue.status shows in the desk once the decision is made.
MIRRORED_STATUS = {REJECTED: "Closed", COMPLETED: "Resolved"}

DECISIONS = {"approve": IN_PROGRESS, "reject": REJECTED}


def effective_owner(property_name: str | None) -> str | None:
	"""Customer owning a property: its own ``unit_owner`` or its nearest parent's."""
	seen: set[str] = set()
	while property_name and property_name not in seen:
		seen.add(property_name)
		row = frappe.db.get_value("Property", property_name, ["unit_owner", "parent_property"], as_dict=True)
		if not row:
			return None
		if row.unit_owner:
			return row.unit_owner
		property_name = row.parent_property
	return None


def is_linked_to(user: str, customer: str | None) -> bool:
	"""The user is a portal user of `customer`, and that Customer is enabled."""
	if not customer or not user or user == "Guest":
		return False
	return customer in get_customers(user)


def can_decide(issue_name: str, user: str | None = None) -> bool:
	"""The user is linked to the property owner and the request still awaits a decision."""
	user = user or frappe.session.user
	row = frappe.db.get_value("Issue", issue_name, ["property_name", "sky_immo_status"], as_dict=True)
	if not row or row.sky_immo_status != AWAITING:
		return False
	return is_linked_to(user, effective_owner(row.property_name))


def set_status(issue_name: str, status: str) -> None:
	"""Write the app status, then mirror it on the desk status, without a Website User save."""
	if status not in STATUSES:
		frappe.throw(_("Unknown maintenance status: {0}").format(status))
	values = {"sky_immo_status": status}
	if status in MIRRORED_STATUS:
		values["status"] = MIRRORED_STATUS[status]
	frappe.db.set_value("Issue", issue_name, values)


@frappe.whitelist(methods=["POST"])
def decide(name: str, decision: str) -> dict:
	"""Approve or reject a maintenance request. Called by the app and by the desk buttons."""
	if decision not in DECISIONS:
		frappe.throw(_("Unknown decision."))
	if not frappe.db.exists("Issue", name):
		frappe.throw(_("Not found"), frappe.DoesNotExistError)

	status = frappe.db.get_value("Issue", name, "sky_immo_status")
	if status != AWAITING:
		frappe.throw(_("This request is no longer awaiting approval."), title=_("Already decided"))
	if not can_decide(name):
		frappe.throw(_("Only the owner of the property can decide on this request."), frappe.PermissionError)

	new_status = DECISIONS[decision]
	set_status(name, new_status)
	frappe.get_doc("Issue", name).add_comment(
		"Info",
		_("{0} by {1} in Sky Immo.").format(
			_("Approved") if decision == "approve" else _("Rejected"),
			frappe.utils.get_fullname(frappe.session.user),
		),
	)
	return {"id": name, "approval": APP_STATUS[new_status]}


@frappe.whitelist(methods=["GET"])
def desk_permissions(name: str) -> dict:
	"""For the Issue form: show the Approve and Reject buttons only to the owner's user."""
	return {"canDecide": can_decide(name)}


def on_issue_update(doc, method=None):
	"""Staff closing or resolving a request in the desk keep the app status in step."""
	current = doc.get("sky_immo_status")
	if current in (None, "", AWAITING, REJECTED):
		return
	if doc.status in ("Resolved", "Closed") and current != COMPLETED:
		frappe.db.set_value("Issue", doc.name, "sky_immo_status", COMPLETED, update_modified=False)


def can_complete(issue_name: str, user: str | None = None) -> bool:
	"""The tenant who made the request, while the owner's approval has it In progress."""
	user = user or frappe.session.user
	row = frappe.db.get_value("Issue", issue_name, ["raised_by", "sky_immo_status"], as_dict=True)
	if not row or row.sky_immo_status != IN_PROGRESS:
		return False
	return (
		bool(row.raised_by)
		and row.raised_by.lower() == (frappe.db.get_value("User", user, "email") or user).lower()
	)


@frappe.whitelist(methods=["POST"])
def complete(name: str) -> dict:
	"""The tenant marks their request as completed. It then shows as Resolved in the desk."""
	row = frappe.db.get_value("Issue", name, ["raised_by", "sky_immo_status"], as_dict=True)
	if not row:
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	user_email = (frappe.db.get_value("User", frappe.session.user, "email") or frappe.session.user).lower()
	if (row.raised_by or "").lower() != user_email:
		frappe.throw(
			_("Only the tenant who made this request can mark it as completed."), frappe.PermissionError
		)
	if row.sky_immo_status != IN_PROGRESS:
		frappe.throw(
			_("A request can be marked as completed only while it is in progress."),
			title=_("Not in progress"),
		)
	set_status(name, COMPLETED)
	frappe.get_doc("Issue", name).add_comment(
		"Info",
		_("Marked as completed by {0} in Sky Immo.").format(frappe.utils.get_fullname(frappe.session.user)),
	)
	return {"id": name, "approval": APP_STATUS[COMPLETED]}
