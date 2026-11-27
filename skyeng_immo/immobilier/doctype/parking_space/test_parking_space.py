import frappe
from frappe.tests.utils import FrappeTestCase

from skyeng_immo.immobilier.doctype.occupant.test_occupant import _property


class TestParkingSpace(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = _property("_TEST IMMO Site", is_group=1)
		cls.unit_a = _property("_TEST IMMO Unit A", parent=cls.site)
		cls.other_site = _property("_TEST IMMO Other Site", is_group=1)
		cls.foreign_unit = _property("_TEST IMMO Foreign Unit", parent=cls.other_site)

	def _space(self, number, **kw):
		payload = {"doctype": "Parking Space", "property": self.site, "parking_number": number}
		payload.update(kw)
		return frappe.get_doc(payload)

	def test_unallocated_space_is_free(self):
		s = self._space("F01").insert()
		self.assertEqual(s.status, "Libre")

	def test_allocated_space_is_attribuee(self):
		s = self._space("F02", allocated_to_unit=self.unit_a).insert()
		self.assertEqual(s.status, "Attribuee")

	def test_cannot_allocate_to_a_unit_on_another_site(self):
		s = self._space("F03", allocated_to_unit=self.foreign_unit)
		self.assertRaises(frappe.ValidationError, s.insert)

	def test_parking_summary_counts_spaces_per_unit(self):
		from skyeng_immo.immobilier.doctype.parking_space.parking_space import parking_summary

		self._space("F05", allocated_to_unit=self.unit_a).insert()
		self._space("F06", allocated_to_unit=self.unit_a).insert()
		self._space("F07").insert()  # not allocated: not in the summary
		spaces = frappe.get_all(
			"Parking Space", filters={"property": self.site, "allocated_to_unit": self.unit_a}, pluck="name"
		)
		vehicles = frappe.db.count("Vehicle", {"parking_space": ["in", spaces], "is_active": 1})

		rows = {row.unit: row for row in parking_summary(self.site)}
		self.assertEqual(set(rows), {self.unit_a})
		self.assertEqual(rows[self.unit_a].spaces, len(spaces))
		self.assertEqual(rows[self.unit_a].vehicles, vehicles)
		self.assertEqual(parking_summary(self.other_site), [])

	def test_out_of_service_survives_allocation(self):
		s = self._space("F04", status="Hors service").insert()
		self.assertEqual(s.status, "Hors service")
