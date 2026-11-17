import frappe
from frappe.translate import get_all_translations

from skyeng_immo import access


@frappe.whitelist(methods=["GET"])
def get_translations() -> dict[str, str]:
	"""Site translations in the signed-in user's language, for the frontend's __()."""
	return get_all_translations(frappe.local.lang)


@frappe.whitelist(methods=["GET"])
def get_properties() -> list[dict]:
	"""Properties in the user's scope, in tree order. The owner is not exposed."""
	return access.get_properties(access.get_scope(), ["name", "parent_property", "is_group", "status"])


@frappe.whitelist(methods=["GET"])
def get_leases() -> list[dict]:
	return access.get_leases(
		access.get_scope(),
		["name", "property", "lease_customer", "start_date", "end_date", "lease_status"],
	)


@frappe.whitelist(methods=["GET"])
def get_invoices() -> list[dict]:
	return access.get_invoices(
		access.get_scope(),
		["name", "lease", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
	)


@frappe.whitelist(methods=["GET"])
def get_maintenance_requests() -> list[dict]:
	return access.get_issues(access.get_scope(), ["name", "subject", "property_name", "status", "creation"])


@frappe.whitelist(methods=["GET"])
def download_invoice_pdf(name: str) -> None:
	"""Send the PDF of an invoice, only if it is in the user's scope (403 otherwise).

	Landlords and tenants have no print permission on Sales Invoice, so the print check
	is lifted for this one render, after the scope check.
	"""
	access.check_invoice(access.get_scope(), name)

	frappe.flags.ignore_print_permissions = True
	try:
		pdf = frappe.get_print("Sales Invoice", name, as_pdf=True)
	finally:
		frappe.flags.ignore_print_permissions = False

	frappe.local.response.filename = f"{name.replace(' ', '-').replace('/', '-')}.pdf"
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "pdf"
