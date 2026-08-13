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


def after_install():
	setup()


def after_migrate():
	setup()


def setup():
	create_roles()
	install_asset_fields()


def create_roles():
	for name, desc in ROLES:
		if frappe.db.exists("Role", name):
			continue
		frappe.get_doc({"doctype": "Role", "role_name": name, "desk_access": 1, "description": desc}).insert(
			ignore_permissions=True
		)


def install_asset_fields():
	"""Skipped when ERPNext's Asset is absent, so the app degrades rather than crashes."""
	if not frappe.db.exists("DocType", "Asset"):
		return
	create_custom_fields(ASSET_CUSTOM_FIELDS, ignore_validate=True)
