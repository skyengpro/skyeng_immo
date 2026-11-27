import frappe
from frappe.utils.jinja_globals import is_rtl

from skyeng_immo.access import is_manager
from skyeng_immo.immobilier.doctype.sky_immo_settings.sky_immo_settings import MODE_SKY, get_operating_mode

no_cache = 1


def get_context(context):
	# A guest gets the app shell: its router shows the app's own sign-in screen (/sky-immo/connexion).
	# The shell carries no data; every read goes through an endpoint that checks the user.
	if is_manager() and get_operating_mode() == MODE_SKY:
		# 302, not frappe.redirect's 301: a cached redirect would outlive a change of mode.
		frappe.flags.redirect_location = "/desk"
		raise frappe.Redirect(302)

	context.boot = get_boot()
	return context


def get_boot() -> dict:
	guest = frappe.session.user == "Guest"
	return {
		# not for a guest: generating one would write the guest session on every page load
		"csrf_token": None if guest else frappe.sessions.get_csrf_token(),
		"site_name": frappe.local.site,
		"session_user": frappe.session.user,
		"lang": frappe.local.lang,
		"text_direction": "rtl" if is_rtl() else "ltr",
	}
