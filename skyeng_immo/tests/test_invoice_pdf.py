from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import set_request

from skyeng_immo.api import download_invoice_pdf
from skyeng_immo.tests.utils import SharedSite


class TestInvoicePdf(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.site = SharedSite()

	def setUp(self):
		super().setUp()
		set_request(method="GET", path="/api/method/skyeng_immo.api.download_invoice_pdf")
		frappe.local.response = frappe._dict()
		# wkhtmltopdf fetches the print CSS from the request host, where no server listens in tests.
		# The HTML it would receive is kept, to check the print format rendered.
		patcher = patch(
			"frappe.utils.pdf.get_pdf", side_effect=lambda html, *a, **kw: b"%PDF-" + html.encode()
		)
		self.get_pdf = patcher.start()
		self.addCleanup(patcher.stop)

	def download(self, user: str, invoice: str):
		with self.set_user(self.site.users[user]):
			download_invoice_pdf(invoice)

	def test_invoice_in_scope_downloads_as_pdf(self):
		s = self.site
		# The tenant, the landlord and the manager each reach 1A's invoice; a third party pays it.
		for user in ("tenant1", "landlord1", "manager"):
			with self.subTest(user=user):
				frappe.local.response = frappe._dict()
				self.download(user, s.invoice_1a)
				self.assertEqual(frappe.local.response.type, "pdf")
				self.assertEqual(frappe.local.response.filename, f"{s.invoice_1a}.pdf")
				self.assertTrue(frappe.local.response.filecontent.startswith(b"%PDF"))
				self.assertIn(s.invoice_1a.encode(), frappe.local.response.filecontent)

	def test_invoice_is_served_under_its_own_name_whatever_the_requested_case(self):
		invoice = self.site.invoice_1a
		self.download("tenant1", invoice.lower())
		self.assertEqual(frappe.local.response.filename, f"{invoice}.pdf")

	def test_invoice_out_of_scope_is_refused_with_403(self):
		s = self.site
		refused = {
			"tenant1": [s.invoice_2a, s.invoice_old],
			"tenant2": [s.invoice_1a],
			"landlord1": [s.invoice_2a],
			"landlord2": [s.invoice_1a, s.invoice_old],
		}
		for user, invoices in refused.items():
			for invoice in invoices:
				with self.subTest(user=user, invoice=invoice):
					with self.assertRaises(frappe.PermissionError) as raised:
						self.download(user, invoice)
					self.assertEqual(raised.exception.http_status_code, 403)
					self.assertFalse(frappe.local.response.get("filecontent"))

	def test_unsubmitted_and_unknown_invoices_are_refused(self):
		for invoice in (self.site.invoice_unsubmitted, "ACC-SINV-DOES-NOT-EXIST"):
			with self.subTest(invoice=invoice), self.assertRaises(frappe.PermissionError):
				self.download("tenant1", invoice)

	def test_print_permission_check_is_restored_after_the_download(self):
		self.download("tenant1", self.site.invoice_1a)
		self.assertFalse(frappe.flags.ignore_print_permissions)

		with self.assertRaises(frappe.PermissionError):
			self.download("tenant1", self.site.invoice_2a)
		self.assertFalse(frappe.flags.ignore_print_permissions)
