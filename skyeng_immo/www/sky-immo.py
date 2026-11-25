import frappe

no_cache = 1


def get_context(context):
	# the page is a static shell: the signed-in user and the CSRF token come from
	# skyeng_immo.sky_immo.api.get_session, so nothing user-specific is ever rendered into it
	context.no_cache = 1
	context.lang = frappe.local.lang or "en"
