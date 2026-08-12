import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Occupant(Document):
	def validate(self):
		self.validate_dates()
		self.sync_from_lease()
		self.set_status()

	def validate_dates(self):
		if self.move_out_date and self.move_in_date:
			if getdate(self.move_out_date) < getdate(self.move_in_date):
				frappe.throw(
					_("La date de sortie ({0}) precede la date d'entree ({1}).").format(
						self.move_out_date, self.move_in_date
					)
				)

		if self.id_expiry and getdate(self.id_expiry) < getdate(today()) and self.status != "Parti":
			# A guard turning someone away is a business decision, not ours -- warn only.
			frappe.msgprint(
				_("La piece d'identite de {0} a expire le {1}.").format(self.full_name, self.id_expiry),
				indicator="orange",
				alert=True,
			)

	def sync_from_lease(self):
		"""The lease is the source of truth for the unit and the paying tenant."""
		if not self.lease:
			return

		lease_property, customer = frappe.db.get_value("Lease", self.lease, ["property", "customer"])
		self.customer = customer

		if self.property and lease_property and self.property != lease_property:
			frappe.throw(
				_("Le bail {0} porte sur {1}, pas sur {2}.").format(
					self.lease, lease_property, self.property
				)
			)
		if not self.property:
			self.property = lease_property

	def set_status(self):
		self.status = "Parti" if self.move_out_date and getdate(self.move_out_date) <= getdate(today()) else "Actif"


def get_active_occupants(property_name: str) -> list[dict]:
	"""Who is currently authorised to be in this unit. Used by the gate register."""
	return frappe.get_all(
		"Occupant",
		filters={"property": property_name, "status": "Actif"},
		fields=["name", "full_name", "occupant_type", "phone", "id_type", "id_number", "photo"],
		order_by="occupant_type, full_name",
	)
