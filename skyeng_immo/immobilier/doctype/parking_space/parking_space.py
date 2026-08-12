import frappe
from frappe import _
from frappe.model.document import Document


class ParkingSpace(Document):
	def validate(self):
		self.validate_allocation()
		self.set_status()

	def validate_allocation(self):
		"""A space can only be allocated to a unit in the same building."""
		if not self.allocated_to_unit:
			return

		parent = frappe.db.get_value("Property", self.allocated_to_unit, "parent_property")
		# The unit is either a child of this building, or is this property itself
		# (a standalone villa owns its own spaces).
		if parent != self.property and self.allocated_to_unit != self.property:
			frappe.throw(
				_("{0} ne depend pas de {1}. Une place ne peut etre attribuee qu'a une unite du meme site.").format(
					self.allocated_to_unit, self.property
				)
			)

		if self.lease:
			lease_property = frappe.db.get_value("Lease", self.lease, "property")
			if lease_property != self.allocated_to_unit:
				frappe.throw(
					_("Le bail {0} porte sur {1}, pas sur {2}.").format(
						self.lease, lease_property, self.allocated_to_unit
					)
				)

	def set_status(self):
		if self.status == "Hors service":
			return
		if self.allocated_to_unit:
			self.status = "Attribuee"
		elif self.status != "Reservee visiteur":
			self.status = "Libre"


@frappe.whitelist()
def parking_summary(property_name: str | None = None) -> list[dict]:
	"""Places par unite - repond a 'combien de voitures par appartement'."""
	conditions = "WHERE p.allocated_to_unit IS NOT NULL"
	values = {}
	if property_name:
		conditions += " AND p.property = %(property)s"
		values["property"] = property_name
	return frappe.db.sql(
		f"""SELECT p.allocated_to_unit AS unit, COUNT(DISTINCT p.name) AS spaces,
			   COUNT(DISTINCT v.name) AS vehicles
			FROM `tabParking Space` p
			LEFT JOIN `tabVehicle` v ON v.parking_space = p.name AND v.is_active = 1
			{conditions}
			GROUP BY p.allocated_to_unit ORDER BY p.allocated_to_unit""",
		values,
		as_dict=True,
	)
