"""Data entry rules the app relies on, checked when staff save in the desk (EP-01, "Desk setup").

* a Property always has an owner: its own ``unit_owner`` or that of one of its parent properties,
  even when it is the company itself. That is what decides which landlord sees it;
* a Lease has a single Customer, used as tenant and as payer on every lease line:
  that is what decides which tenant sees it and its invoices.
"""

import frappe
from frappe import _


def validate_property(doc, method=None):
	if not doc.unit_owner and not _parent_has_owner(doc.get("parent_property")):
		frappe.throw(
			_(
				"Please set the owner (Unit Owner) of {0}, or of one of its parent properties. Use the company's own Customer when it owns the property."
			).format(frappe.bold(doc.name1 or doc.name)),
			title=_("Owner missing"),
		)


def _parent_has_owner(parent: str | None) -> bool:
	from .maintenance import effective_owner

	return bool(effective_owner(parent))


def validate_lease(doc, method=None):
	customer = doc.customer or doc.lease_customer
	if not customer:
		return  # PropMS already asks for it before invoicing.
	if doc.lease_customer and doc.customer and doc.lease_customer != doc.customer:
		frappe.throw(
			_(
				"A lease has a single tenant: Customer ({0}) and Lease Customer ({1}) must be the same."
			).format(doc.customer, doc.lease_customer),
			title=_("Several customers on one lease"),
		)
	doc.customer = doc.lease_customer = customer

	for row in doc.get("lease_item") or []:
		if not row.paid_by:
			row.paid_by = customer
		elif row.paid_by != customer:
			frappe.throw(
				_("Row {0}: {1} is paid by {2}, but the tenant of this lease is {3}.").format(
					row.idx, row.lease_item, row.paid_by, customer
				),
				title=_("Several customers on one lease"),
			)
