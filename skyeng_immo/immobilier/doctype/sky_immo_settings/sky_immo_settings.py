import frappe
from frappe.model.document import Document

MODE_SKY = "Sky owns an instance"
MODE_CUSTOMER = "A customer owns an instance"


class SkyImmoSettings(Document):
	pass


def get_operating_mode() -> str:
	return frappe.db.get_single_value("Sky Immo Settings", "operating_mode") or MODE_SKY
