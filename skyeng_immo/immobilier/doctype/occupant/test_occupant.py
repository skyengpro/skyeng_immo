import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


def _property(name, parent=None, is_group=0):
	if frappe.db.exists("Property", name):
		return name
	company = frappe.db.get_value("Company", {}, "name")
	return (
		frappe.get_doc(
			{
				"doctype": "Property",
				"name1": name,
				"is_group": is_group,
				"parent_property": parent,
				"company": company,
				"cost_center": frappe.db.get_value("Cost Center", {"is_group": 0}, "name"),
				"status": "On Lease",
			}
		)
		.insert(ignore_permissions=True)
		.name
	)


class TestOccupant(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.unit_a = _property("_TEST IMMO Unit A")
		cls.unit_b = _property("_TEST IMMO Unit B")

	def _occupant(self, **kw):
		payload = {
			"doctype": "Occupant",
			"full_name": "_TEST Occupant",
			"occupant_type": "Locataire titulaire",
			"property": self.unit_a,
			"move_in_date": add_days(today(), -30),
		}
		payload.update(kw)
		return frappe.get_doc(payload)

	def test_status_is_active_without_move_out(self):
		occ = self._occupant().insert()
		self.assertEqual(occ.status, "Actif")

	def test_status_becomes_parti_after_move_out(self):
		occ = self._occupant(move_out_date=add_days(today(), -1)).insert()
		self.assertEqual(occ.status, "Parti")

	def test_future_move_out_is_still_active(self):
		occ = self._occupant(move_out_date=add_days(today(), 30)).insert()
		self.assertEqual(occ.status, "Actif")

	def test_move_out_before_move_in_is_rejected(self):
		occ = self._occupant(move_in_date=today(), move_out_date=add_days(today(), -5))
		self.assertRaises(frappe.ValidationError, occ.insert)

	def test_get_active_occupants_excludes_departed(self):
		from skyeng_immo.immobilier.doctype.occupant.occupant import get_active_occupants

		self._occupant(full_name="_TEST Present").insert()
		self._occupant(full_name="_TEST Departed", move_out_date=add_days(today(), -2)).insert()
		names = [o["full_name"] for o in get_active_occupants(self.unit_a)]
		self.assertIn("_TEST Present", names)
		self.assertNotIn("_TEST Departed", names)
