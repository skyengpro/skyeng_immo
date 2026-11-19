import frappe
from frappe.translate import get_all_translations


@frappe.whitelist(methods=["GET"])
def get_translations() -> dict[str, str]:
	"""Site translations in the signed-in user's language, for the frontend's __()."""
	return get_all_translations(frappe.local.lang)
