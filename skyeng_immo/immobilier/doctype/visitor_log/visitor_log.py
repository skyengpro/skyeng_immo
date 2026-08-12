import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime, time_diff_in_seconds


class VisitorLog(Document):
	def validate(self):
		self.validate_movement()
		self.validate_host()
		self.set_duration_and_status()

	def validate_movement(self):
		if self.check_in and get_datetime(self.check_in) > now_datetime():
			frappe.throw(_("L'heure d'entree est dans le futur."))

		if self.check_out and self.check_in:
			if get_datetime(self.check_out) < get_datetime(self.check_in):
				frappe.throw(
					_("La sortie ({0}) precede l'entree ({1}).").format(self.check_out, self.check_in)
				)

	def validate_host(self):
		"""A host must actually live in the unit being visited."""
		if not self.host_occupant:
			return

		host_property, host_status = frappe.db.get_value(
			"Occupant", self.host_occupant, ["property", "status"]
		)
		if host_property != self.visiting_property:
			frappe.throw(
				_("{0} n'occupe pas {1} mais {2}.").format(
					self.host_occupant, self.visiting_property, host_property
				)
			)
		if host_status != "Actif":
			frappe.msgprint(
				_("L'hote {0} n'est plus un occupant actif.").format(self.host_occupant),
				indicator="orange",
				alert=True,
			)

	def set_duration_and_status(self):
		if self.check_out and self.check_in:
			self.duration_minutes = int(
				time_diff_in_seconds(self.check_out, self.check_in) // 60
			)
			self.status = "Sorti"
		else:
			self.duration_minutes = 0
			self.status = "A l'interieur"


@frappe.whitelist()
def check_out_visitor(name: str) -> str:
	"""One-click sortie from the gate. Returns the visit duration in minutes."""
	doc = frappe.get_doc("Visitor Log", name)
	if doc.check_out:
		frappe.throw(_("{0} est deja sorti a {1}.").format(doc.visitor_name, doc.check_out))
	doc.check_out = now_datetime()
	doc.save()
	return str(doc.duration_minutes)


@frappe.whitelist()
def currently_inside(property_name: str | None = None) -> list[dict]:
	"""Everyone still on site. The question a guard actually asks."""
	filters = {"status": "A l'interieur"}
	if property_name:
		filters["visiting_property"] = property_name
	return frappe.get_all(
		"Visitor Log",
		filters=filters,
		fields=["name", "visitor_name", "visiting_property", "host_occupant", "check_in", "badge_number", "vehicle_plate"],
		order_by="check_in",
	)
