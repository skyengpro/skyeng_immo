import frappe
from frappe.translate import get_all_translations

from skyeng_immo.access import check_invoice, get_scope


@frappe.whitelist(methods=["GET"])
def get_translations() -> dict[str, str]:
	"""Site translations in the signed-in user's language, for the frontend's __()."""
	return get_all_translations(frappe.local.lang)


@frappe.whitelist(methods=["GET"])
def download_invoice_pdf(name: str) -> None:
	"""Send the PDF of an invoice, only if it is in the user's scope (403 otherwise).

	Landlords and tenants have no print permission on Sales Invoice, so the print check
	is lifted for this one render, after the scope check.
	"""
	check_invoice(get_scope(), name)

	frappe.flags.ignore_print_permissions = True
	try:
		pdf = frappe.get_print("Sales Invoice", name, as_pdf=True)
	finally:
		frappe.flags.ignore_print_permissions = False

	frappe.local.response.filename = f"{name.replace(' ', '-').replace('/', '-')}.pdf"
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"
