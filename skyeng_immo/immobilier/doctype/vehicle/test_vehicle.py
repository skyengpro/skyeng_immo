import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from skyeng_immo.immobilier.doctype.occupant.test_occupant import _property


class TestVehicle(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = _property("_TEST IMMO Site", is_group=1)
		cls.unit_a = _property("_TEST IMMO Unit A", parent=cls.site)
		cls.unit_b = _property("_TEST IMMO Unit B", parent=cls.site)
		cls.occ = frappe.get_doc(
			{
				"doctype": "Occupant",
				"full_name": "_TEST Driver",
				"occupant_type": "Locataire titulaire",
				"property": cls.unit_a,
				"move_in_date": add_days(today(), -10),
			}
		).insert(ignore_permissions=True)
		cls.space = frappe.get_doc(
			{
				"doctype": "Parking Space",
				"property": cls.site,
				"parking_number": "T01",
				"allocated_to_unit": cls.unit_a,
			}
		).insert(ignore_permissions=True)

	def _vehicle(self, plate, **kw):
		payload = {
			"doctype": "Vehicle",
			"plate_number": plate,
			"owner_occupant": self.occ.name,
			"vehicle_type": "Voiture",
		}
		payload.update(kw)
		return frappe.get_doc(payload)

	def test_plate_is_normalised(self):
		v = self._vehicle("  lt-123-a   ").insert()
		self.assertEqual(v.plate_number, "LT-123-A")

	def test_property_filled_from_occupant(self):
		v = self._vehicle("LT-200-B").insert()
		self.assertEqual(v.property, self.unit_a)

	def test_space_cannot_be_double_booked(self):
		self._vehicle("LT-300-C", parking_space=self.space.name).insert()
		second = self._vehicle("LT-301-D", parking_space=self.space.name)
		self.assertRaises(frappe.ValidationError, second.insert)

	def test_lookup_plate_finds_resident(self):
		from skyeng_immo.immobilier.doctype.vehicle.vehicle import lookup_plate

		self._vehicle("LT-400-E").insert()
		found = lookup_plate("lt-400-e")
		self.assertTrue(found["known"])
		self.assertEqual(found["occupant_name"], "_TEST Driver")

	def test_lookup_plate_unknown(self):
		from skyeng_immo.immobilier.doctype.vehicle.vehicle import lookup_plate

		self.assertFalse(lookup_plate("XX-999-Z")["known"])
