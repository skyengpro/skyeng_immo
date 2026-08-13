import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_to_date, now_datetime, today

from skyeng_immo.immobilier.doctype.occupant.test_occupant import _property


class TestVisitorLog(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.unit_a = _property("_TEST IMMO Unit A")
		cls.unit_b = _property("_TEST IMMO Unit B")
		cls.host = frappe.get_doc(
			{
				"doctype": "Occupant",
				"full_name": "_TEST Host",
				"occupant_type": "Locataire titulaire",
				"property": cls.unit_a,
				"move_in_date": add_days(today(), -60),
			}
		).insert(ignore_permissions=True)

	def _visit(self, **kw):
		payload = {
			"doctype": "Visitor Log",
			"visitor_name": "_TEST Visitor",
			"visiting_property": self.unit_a,
			"purpose": "Visite privee",
			"check_in": add_to_date(now_datetime(), hours=-2),
		}
		payload.update(kw)
		return frappe.get_doc(payload)

	def test_open_visit_is_inside(self):
		v = self._visit().insert()
		self.assertEqual(v.status, "A l'interieur")
		self.assertEqual(v.duration_minutes, 0)

	def test_duration_computed_on_check_out(self):
		start = add_to_date(now_datetime(), hours=-3)
		v = self._visit(check_in=start, check_out=add_to_date(start, minutes=45)).insert()
		self.assertEqual(v.status, "Sorti")
		self.assertEqual(v.duration_minutes, 45)

	def test_check_out_before_check_in_is_rejected(self):
		start = now_datetime()
		v = self._visit(check_in=start, check_out=add_to_date(start, minutes=-30))
		self.assertRaises(frappe.ValidationError, v.insert)

	def test_future_check_in_is_rejected(self):
		v = self._visit(check_in=add_to_date(now_datetime(), hours=4))
		self.assertRaises(frappe.ValidationError, v.insert)

	def test_host_must_occupy_the_visited_unit(self):
		"""The guard that makes the register trustworthy."""
		v = self._visit(visiting_property=self.unit_b, host_occupant=self.host.name)
		self.assertRaises(frappe.ValidationError, v.insert)

	def test_currently_inside_reflects_check_out(self):
		from skyeng_immo.immobilier.doctype.visitor_log.visitor_log import (
			check_out_visitor,
			currently_inside,
		)

		v = self._visit(visitor_name="_TEST Still Here").insert()
		inside = [x["name"] for x in currently_inside(self.unit_a)]
		self.assertIn(v.name, inside)

		check_out_visitor(v.name)
		inside = [x["name"] for x in currently_inside(self.unit_a)]
		self.assertNotIn(v.name, inside)

	def test_double_check_out_is_rejected(self):
		from skyeng_immo.immobilier.doctype.visitor_log.visitor_log import check_out_visitor

		v = self._visit().insert()
		check_out_visitor(v.name)
		self.assertRaises(frappe.ValidationError, check_out_visitor, v.name)
