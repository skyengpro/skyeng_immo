from urllib.parse import urlencode

import frappe
from frappe.utils.jinja_globals import is_rtl

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		# 302, not frappe.redirect's 301: a cached redirect would outlive the login.
		frappe.flags.redirect_location = "/login?" + urlencode({"redirect-to": frappe.request.path})
		raise frappe.Redirect(302)

	context.boot = get_boot()
	return context


def get_boot() -> dict:
	return {
		"csrf_token": frappe.sessions.get_csrf_token(),
		"site_name": frappe.local.site,
		"session_user": frappe.session.user,
		"lang": frappe.local.lang,
		"text_direction": "rtl" if is_rtl() else "ltr",
	}
