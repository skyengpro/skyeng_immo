"""Invite a Customer to Sky-immo from Desk.

The inviter needs a staff role and read access to the Customer. Only after both checks does the
code create the User and the Portal User row with `ignore_permissions`, since the staff member
usually cannot write either.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime

from skyeng_immo.access import LANDLORD, MANAGER_ROLES, TENANT


@frappe.whitelist(methods=["POST"])
def invite_customer(customer: str) -> dict:
	"""Create or reuse the user of `customer`, link them and email a link to set a password."""
	frappe.only_for(MANAGER_ROLES)
	frappe.has_permission("Customer", "read", doc=customer, throw=True)

	if frappe.db.get_value("Customer", customer, "disabled"):
		frappe.throw(_("Customer {0} is disabled.").format(customer))

	email = get_customer_email(customer)
	if not email:
		frappe.throw(
			_("Customer {0} has no email address. Add one to their primary contact.").format(customer)
		)

	roles = get_app_roles(customer)
	if not roles:
		frappe.throw(_("Customer {0} owns no property and has no active lease.").format(customer))

	user, created = get_or_create_user(email, frappe.db.get_value("Customer", customer, "customer_name"))
	user.append_roles(*roles)
	user.save(ignore_permissions=True)
	link_portal_user(customer, user.name)

	try:
		user.send_welcome_mail_to_user()
	except frappe.OutgoingEmailError:
		frappe.throw(_("No outgoing email account is set up, so the invitation cannot be sent."))

	return {"user": user.name, "roles": roles, "created": created}


def get_customer_email(customer: str) -> str:
	"""Email of the primary contact. Customer.email_id only copies it when the Customer is saved."""
	contact, stored = frappe.db.get_value("Customer", customer, ["customer_primary_contact", "email_id"])
	live = frappe.db.get_value("Contact", contact, "email_id") if contact else None
	return (live or stored or "").strip().lower()


def get_app_roles(customer: str) -> list[str]:
	"""Landlord if the customer owns a property, Tenant if they have an active lease.

	Owning a unit through its parent means the parent names the customer, so no tree walk is needed.
	"""
	roles = []
	if frappe.db.exists("Property", {"unit_owner": customer}):
		roles.append(LANDLORD)
	if frappe.db.exists("Lease", {"lease_customer": customer, "lease_status": "Active"}):
		roles.append(TENANT)
	return roles


def get_or_create_user(email: str, full_name: str):
	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
		if not user.enabled:
			frappe.throw(_("User {0} is disabled. Enable them before sending an invitation.").format(email))
		return user, False

	user = frappe.get_doc(
		{"doctype": "User", "email": email, "first_name": full_name, "send_welcome_email": 0}
	)
	user.insert(ignore_permissions=True)
	return user, True


def link_portal_user(customer: str, user: str) -> None:
	"""Add `user` to the Customer's Portal Users, once.

	The row is inserted on its own instead of saving the Customer: ERPNext would give the
	user its Customer role, which opens the ERPNext portal beside this app.
	"""
	filters = {"parenttype": "Customer", "parentfield": "portal_users", "parent": customer}
	if frappe.db.exists("Portal User", {**filters, "user": user}):
		return
	idx = frappe.db.count("Portal User", filters) + 1
	frappe.get_doc({"doctype": "Portal User", **filters, "user": user, "idx": idx}).insert(
		ignore_permissions=True
	)
	# Saving a Customer form opened before this row existed would delete it. A new `modified`
	# makes that save fail with a "reload the document" error instead.
	frappe.db.set_value("Customer", customer, "modified", now_datetime(), update_modified=False)
	frappe.clear_document_cache("Customer", customer)
