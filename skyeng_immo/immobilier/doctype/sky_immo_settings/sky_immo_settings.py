import frappe
from frappe.model.document import Document

MODE_SKY = "Sky owns an instance"
MODE_CUSTOMER = "A customer owns an instance"


class SkyImmoSettings(Document):
	def on_update(self):
		# Frappe caches each user's landing page, which depends on the mode.
		frappe.cache.delete_key("home_page")


def get_operating_mode() -> str:
	return frappe.db.get_single_value("Sky Immo Settings", "operating_mode") or MODE_SKY
