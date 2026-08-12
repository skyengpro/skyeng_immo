import frappe
from frappe import _
from frappe.model.document import Document


class Vehicle(Document):
	def validate(self):
		self.normalise_plate()
		self.sync_from_occupant()
		self.validate_parking_space()

	def normalise_plate(self):
		"""Plates are matched by eye at a barrier; store one canonical form."""
		if self.plate_number:
			self.plate_number = " ".join(self.plate_number.upper().split())

	def sync_from_occupant(self):
		if not self.owner_occupant:
			return
		occupant_property, status = frappe.db.get_value(
			"Occupant", self.owner_occupant, ["property", "status"]
		)
		self.property = occupant_property
		if status != "Actif":
			frappe.msgprint(
				_("{0} n'est plus un occupant actif.").format(self.owner_occupant),
				indicator="orange",
				alert=True,
			)

	def validate_parking_space(self):
		if not self.parking_space:
			return

		taken_by = frappe.db.get_value(
			"Vehicle",
			{"parking_space": self.parking_space, "name": ("!=", self.name), "is_active": 1},
			"name",
		)
		if taken_by:
			frappe.throw(
				_("La place {0} est deja occupee par le vehicule {1}.").format(
					self.parking_space, taken_by
				)
			)

		allocated_unit = frappe.db.get_value("Parking Space", self.parking_space, "allocated_to_unit")
		if allocated_unit and self.property and allocated_unit != self.property:
			frappe.throw(
				_("La place {0} est attribuee a {1}, pas a {2}.").format(
					self.parking_space, allocated_unit, self.property
				)
			)


@frappe.whitelist()
def lookup_plate(plate: str) -> dict:
	"""Barrier lookup: whose car is this, and is it expected here?"""
	plate = " ".join((plate or "").upper().split())
	v = frappe.db.get_value(
		"Vehicle",
		{"plate_number": plate},
		["name", "owner_occupant", "property", "parking_space", "make", "model", "color", "is_active"],
		as_dict=True,
	)
	if v:
		v["known"] = True
		v["occupant_name"] = frappe.db.get_value("Occupant", v["owner_occupant"], "full_name")
		return v

	# Not a resident vehicle - is it a visitor currently on site?
	visit = frappe.db.get_value(
		"Visitor Log",
		{"vehicle_plate": plate, "status": "A l'interieur"},
		["name", "visitor_name", "visiting_property", "check_in"],
		as_dict=True,
	)
	return {"known": False, "plate_number": plate, "visitor": visit}
