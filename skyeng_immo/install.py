"""Everything this app needs that is not a DocType.

Runs on both install and migrate, and is idempotent, so an existing site
picks up additions without a reinstall. The alternative -- leaving these as
site data -- means a fresh install yields the DocTypes and nothing else:
no warranty field, no roles, so the permissions on our own DocTypes point at
roles that do not exist.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

# ERPNext tracks warranty on Serial No, never on Asset. Property management
# cares about warranty per equipment (ascenseur, groupe electrogene), so we
# add it. `immo_property` ties the Asset to the unit it serves; PropMS's
# Property.unit_assets gives the forward link but nothing points back.
ASSET_CUSTOM_FIELDS = {
	"Asset": [
		{
			"fieldname": "warranty_expiry_date",
			"label": "Expiration garantie",
			"fieldtype": "Date",
			"insert_after": "purchase_date",
			"description": "ERPNext ne suit la garantie que sur Serial No.",
		},
		{
			"fieldname": "immo_property",
			"label": "Unite / site",
			"fieldtype": "Link",
			"options": "Property",
			"insert_after": "location",
			"description": "Bien immobilier auquel l'equipement est rattache.",
		},
	]
}

# Referenced by the permissions on our DocTypes. Frappe auto-creates roles it
# finds in a DocType's permissions, but not the ones we only reference from
# data (Technicien is used by Asset Maintenance Team members).
ROLES = [
	("Gardien", "Guerite: enregistre les visiteurs, consulte les occupants."),
	("Property Manager", "Gestion locative complete."),
	("Technicien", "Interventions et maintenance des equipements."),
]

# Mon Immo app roles. No desk access: landlords and tenants only use /mon-immo,
# and read their data through skyeng_immo.mon_immo.api, never through doctypes.
APP_ROLES = [
	("Landlord", "Mon Immo: proprietaire, voit ses biens, baux, factures et paiements."),
	("Tenant", "Mon Immo: locataire, voit son bail et ses factures, signale un probleme."),
]


def after_install():
	setup()


def after_migrate():
	setup()


def setup():
	create_roles()
	install_asset_fields()
	setup_mon_immo()


def create_roles():
	for roles, desk_access in ((ROLES, 1), (APP_ROLES, 0)):
		for name, desc in roles:
			if frappe.db.exists("Role", name):
				continue
			frappe.get_doc(
				{"doctype": "Role", "role_name": name, "desk_access": desk_access, "description": desc}
			).insert(ignore_permissions=True)


def setup_mon_immo():
	"""Issue types and priorities the tenant's request form maps to, and the email templates."""
	from skyeng_immo.mon_immo.data import ISSUE_CATEGORIES
	from skyeng_immo.mon_immo.notifications import ensure_email_templates

	if frappe.db.exists("DocType", "Issue Type"):
		for issue_type in ISSUE_CATEGORIES.values():
			if not frappe.db.exists("Issue Type", issue_type):
				frappe.get_doc({"doctype": "Issue Type", "__newname": issue_type}).insert(
					ignore_permissions=True
				)
	if frappe.db.exists("DocType", "Issue Priority"):
		for priority in ("Medium", "High"):
			if not frappe.db.exists("Issue Priority", priority):
				frappe.get_doc({"doctype": "Issue Priority", "__newname": priority}).insert(
					ignore_permissions=True
				)
	ensure_email_templates()

	# Accounts created before the User hook existed: open the app after sign-in.
	app_users = frappe.get_all(
		"Has Role",
		filters={"role": ["in", [name for name, _desc in APP_ROLES]], "parenttype": "User"},
		pluck="parent",
	)
	if app_users:
		frappe.db.set_value(
			"User",
			{"name": ["in", app_users], "user_type": "Website User", "default_app": ["in", ["", None]]},
			"default_app",
			"skyeng_immo",
			update_modified=False,
		)


def install_asset_fields():
	"""Skipped when ERPNext's Asset is absent, so the app degrades rather than crashes."""
	if not frappe.db.exists("DocType", "Asset"):
		return
	create_custom_fields(ASSET_CUSTOM_FIELDS, ignore_validate=True)
