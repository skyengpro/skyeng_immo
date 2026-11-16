"""Staff give a landlord or a tenant access to the app, from the Customer form.

One click does the whole account setup: the User (website user, Landlord or
Tenant role, language), the Customer's *Portal Users* row that ties the
account to its data, and Frappe's welcome email. The link in that email lets
the person choose a password; Frappe then opens the app (``role_home_page``).
"""

import frappe
from frappe import _
from frappe.utils import validate_email_address

from .access import LANDLORD_ROLE, MANAGER_ROLES, TENANT_ROLE

APP_ROLES = (LANDLORD_ROLE, TENANT_ROLE)


@frappe.whitelist(methods=["POST"])
def invite_to_app(customer: str, email: str, role: str, language: str = "fr") -> dict:
	frappe.only_for(MANAGER_ROLES)
	if role not in APP_ROLES:
		frappe.throw(_("Role must be Landlord or Tenant."))
	email = (email or "").strip().lower()
	if not validate_email_address(email):
		frappe.throw(_("{0} is not a valid email address.").format(email))
	if language not in ("fr", "en"):
		language = "fr"

	customer_doc = frappe.get_doc("Customer", customer)
	created = False
	user = frappe.db.get_value("User", {"name": email}) or frappe.db.get_value("User", {"email": email})
	if user:
		user_doc = frappe.get_doc("User", user)
		if role not in frappe.get_roles(user):
			user_doc.add_roles(role)
	else:
		first, _sep, last = (customer_doc.customer_name or email).partition(" ")
		user_doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first,
				"last_name": last,
				"language": language,
				# The welcome email is sent below, once the portal link exists.
				"send_welcome_email": 0,
				"roles": [{"role": role}],
			}
		)
		user_doc.flags.ignore_password_policy = True
		user_doc.insert(ignore_permissions=True)
		created = True

	if not any(row.user == user_doc.name for row in customer_doc.get("portal_users") or []):
		customer_doc.append("portal_users", {"user": user_doc.name})
		customer_doc.save(ignore_permissions=True)

	# New account, or one that never signed in: (re)send the invitation.
	sent, email_error = False, None
	if created or not user_doc.last_login:
		try:
			user_doc.send_welcome_mail_to_user()
			sent = True
		except frappe.OutgoingEmailError:
			# The account and its link are kept: staff fix the email setup, then click again.
			frappe.clear_last_message()
			email_error = _(
				"The account is ready, but the invitation could not be sent: no outgoing email account is set up."
			)

	return {"user": user_doc.name, "created": created, "invitationSent": sent, "emailError": email_error}
