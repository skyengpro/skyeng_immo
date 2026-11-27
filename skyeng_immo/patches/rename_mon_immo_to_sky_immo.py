"""The app was first called Mon Immo: carry its records over to the Sky Immo name.

Email templates are renamed, not recreated, so wording staff edited in the desk is kept.
"""

import frappe

OLD, NEW = "Mon Immo", "Sky Immo"


def execute():
	for name in frappe.get_all("Email Template", filters={"name": ["like", f"{OLD} - %"]}, pluck="name"):
		new_name = NEW + name[len(OLD) :]
		if frappe.db.exists("Email Template", new_name):
			continue
		frappe.rename_doc("Email Template", name, new_name, force=True)
		template = frappe.get_doc("Email Template", new_name)
		template.subject = (template.subject or "").replace(OLD, NEW)
		template.response = (template.response or "").replace(OLD, NEW)
		template.response_html = (template.response_html or "").replace(OLD, NEW)
		template.save(ignore_permissions=True)

	# Jobs registered under the old module path; migrate registers them again under the new one.
	frappe.db.delete("Scheduled Job Type", {"method": ["like", "skyeng_immo.mon_immo.%"]})
