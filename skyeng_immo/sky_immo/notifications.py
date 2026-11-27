"""The three Sky Immo emails that follow invoices and payments (EP-01, "Emails").

* reminder to the tenant a few days before a due date (daily job);
* receipt to the tenant when a payment is recorded in the desk;
* notice to the landlord when a payment is recorded in the desk.

The invitation is Frappe's own welcome email (see :mod:`.invite`).

Wording lives in Email Templates created by ``install.py``, one per email and
language (``Sky Immo - Receipt (fr)``…), so staff edit it in the desk. Who
receives what is decided here, because ERPNext Notifications cannot reach
"the app accounts of the Customer who owns this property".
"""

import frappe
from frappe.translate import print_language
from frappe.utils import add_days, fmt_money, formatdate, get_url, getdate, today

from skyeng_immo.access import LANDLORD as LANDLORD_ROLE
from skyeng_immo.access import TENANT as TENANT_ROLE

REMINDER_DAYS = 5
APP_ROUTE = "/sky-immo"

TEMPLATES = {
	"Due reminder": {
		"fr": (
			"Rappel : loyer de {{ amount }} à payer avant le {{ due_date }}",
			"<p>Bonjour {{ name }},</p>"
			"<p>Votre loyer pour <b>{{ property }}</b> ({{ period }}) arrive à échéance le "
			"<b>{{ due_date }}</b>. Montant restant à payer : <b>{{ amount }}</b>.</p>"
			"<p>Facture n° {{ invoice }}.</p>"
			'<p><a href="{{ app_url }}">Ouvrir Sky Immo</a></p>',
		),
		"en": (
			"Reminder: rent of {{ amount }} due by {{ due_date }}",
			"<p>Hello {{ name }},</p>"
			"<p>Your rent for <b>{{ property }}</b> ({{ period }}) is due on "
			"<b>{{ due_date }}</b>. Amount left to pay: <b>{{ amount }}</b>.</p>"
			"<p>Invoice no. {{ invoice }}.</p>"
			'<p><a href="{{ app_url }}">Open Sky Immo</a></p>',
		),
	},
	"Receipt": {
		"fr": (
			"Reçu de paiement : {{ amount }}",
			"<p>Bonjour {{ name }},</p>"
			"<p>Nous avons bien reçu votre paiement de <b>{{ amount }}</b> le {{ date }} "
			"pour {{ property }}.</p>"
			"<p>Facture(s) réglée(s) : {{ invoices }}. Le reçu est joint à cet e-mail.</p>"
			'<p><a href="{{ app_url }}">Ouvrir Sky Immo</a></p>',
		),
		"en": (
			"Payment receipt: {{ amount }}",
			"<p>Hello {{ name }},</p>"
			"<p>We have received your payment of <b>{{ amount }}</b> on {{ date }} "
			"for {{ property }}.</p>"
			"<p>Invoice(s) paid: {{ invoices }}. The receipt is attached to this email.</p>"
			'<p><a href="{{ app_url }}">Open Sky Immo</a></p>',
		),
	},
	"Payment notice": {
		"fr": (
			"Paiement reçu de {{ tenant }} : {{ amount }}",
			"<p>Bonjour {{ name }},</p>"
			"<p>{{ tenant }} a payé <b>{{ amount }}</b> le {{ date }} pour {{ property }}.</p>"
			"<p>Facture(s) : {{ invoices }}.</p>"
			'<p><a href="{{ app_url }}">Ouvrir Sky Immo</a></p>',
		),
		"en": (
			"Payment received from {{ tenant }}: {{ amount }}",
			"<p>Hello {{ name }},</p>"
			"<p>{{ tenant }} paid <b>{{ amount }}</b> on {{ date }} for {{ property }}.</p>"
			"<p>Invoice(s): {{ invoices }}.</p>"
			'<p><a href="{{ app_url }}">Open Sky Immo</a></p>',
		),
	},
}


def template_name(key: str, lang: str) -> str:
	return f"Sky Immo - {key} ({lang})"


def built_in_template(key: str, lang: str):
	"""The app's own wording of an email, as an (unsaved) Email Template."""
	subject, body = TEMPLATES[key][lang]
	return frappe.get_doc(
		{
			"doctype": "Email Template",
			"name": template_name(key, lang),
			"subject": subject,
			"use_html": 1,
			"response_html": body,
		}
	)


def ensure_email_templates():
	"""Create missing templates. Existing ones are left alone: staff may have edited them."""
	for key, languages in TEMPLATES.items():
		for lang in languages:
			if not frappe.db.exists("Email Template", template_name(key, lang)):
				built_in_template(key, lang).insert(ignore_permissions=True)


# --------------------------------------------------------------------------- #
# Recipients                                                                   #
# --------------------------------------------------------------------------- #


def app_users_of(customer: str, role: str) -> list[frappe._dict]:
	"""Enabled accounts that are portal users of the Customer and hold ``role``.

	Same link as the app's access (`skyeng_immo.access.get_customers`): Portal Users only.
	"""
	users = set(
		frappe.get_all(
			"Portal User",
			filters={"parent": customer, "parenttype": "Customer", "parentfield": "portal_users"},
			pluck="user",
		)
	)
	users.discard(None)
	if not users:
		return []
	with_role = set(
		frappe.get_all(
			"Has Role",
			filters={"parent": ["in", list(users)], "parenttype": "User", "role": role},
			pluck="parent",
			ignore_permissions=True,
		)
	)
	return frappe.get_all(
		"User",
		filters={"name": ["in", list(with_role) or [""]], "enabled": 1},
		fields=["name", "email", "first_name", "language"],
		ignore_permissions=True,
	)


def tenant_recipients(customer: str) -> list[frappe._dict]:
	"""The tenant's app accounts, or the Customer's own email when they have none."""
	users = app_users_of(customer, TENANT_ROLE)
	if users:
		return users
	email, name, language = frappe.db.get_value(
		"Customer", customer, ["email_id", "customer_name", "language"]
	) or (None, None, None)
	return [frappe._dict(email=email, first_name=name, language=language)] if email else []


def owner_of(property_name: str | None) -> str | None:
	"""``unit_owner`` of the property, or of the nearest building above it."""
	seen = set()
	while property_name and property_name not in seen:
		seen.add(property_name)
		owner, parent = frappe.db.get_value("Property", property_name, ["unit_owner", "parent_property"]) or (
			None,
			None,
		)
		if owner:
			return owner
		property_name = parent
	return None


def landlord_recipients(property_name: str | None) -> list[frappe._dict]:
	"""Landlord accounts of the property; property managers for the company's own properties."""
	owner = owner_of(property_name)
	users = app_users_of(owner, LANDLORD_ROLE) if owner else []
	if users:
		return users
	managers = frappe.get_all(
		"Has Role",
		filters={
			"role": "Property Manager",
			"parenttype": "User",
			"parent": ["not in", ["Administrator", "Guest"]],
		},
		pluck="parent",
		ignore_permissions=True,
	)
	if not managers:
		return []
	return frappe.get_all(
		"User",
		filters={"name": ["in", managers], "enabled": 1, "user_type": "System User"},
		fields=["name", "email", "first_name", "language"],
		ignore_permissions=True,
	)


# --------------------------------------------------------------------------- #
# Sending                                                                      #
# --------------------------------------------------------------------------- #


def _render(key: str, lang: str, context: dict) -> tuple[str, str]:
	"""Subject and body of the email, rendered by Frappe's Email Template in its sandboxed Jinja.

	The template staff edited in the desk (checked by Email Template.validate on save), else the
	app's own wording.
	"""
	name = template_name(key, lang)
	template = (
		frappe.get_doc("Email Template", name)
		if frappe.db.exists("Email Template", name)
		else built_in_template(key, lang)
	)
	return template.get_formatted_subject(context), template.get_formatted_response(context)


def send(key: str, recipients: list, context: dict, reference: tuple[str, str], attach=None):
	"""One email per recipient, in their language. ``attach(lang)`` returns attachments."""
	for recipient in recipients:
		if not recipient.email:
			continue
		lang = (recipient.language or "fr")[:2]
		lang = lang if lang in ("fr", "en") else "fr"
		with print_language(lang):
			args = {**context(lang), "name": recipient.first_name or ""}
			subject, message = _render(key, lang, args)
			try:
				frappe.sendmail(
					recipients=[recipient.email],
					subject=subject,
					message=message,
					attachments=attach(lang) if attach else None,
					reference_doctype=reference[0],
					reference_name=reference[1],
				)
			except frappe.OutgoingEmailError:
				frappe.clear_last_message()
				frappe.log_error(
					f"Sky Immo: no outgoing email account, {key} not sent",
					reference_doctype=reference[0],
					reference_name=reference[1],
				)
				return


def _money(amount, currency):
	return fmt_money(amount, currency=currency)


def _property_label(property_name: str | None) -> str:
	if not property_name:
		return ""
	parent = frappe.db.get_value("Property", property_name, "parent_property")
	return f"{parent} · {property_name}" if parent else property_name


def on_payment_entry_submit(doc, method=None):
	"""doc_events hook: queue the receipt and the landlord notice after the commit."""
	if doc.payment_type != "Receive" or doc.party_type != "Customer" or frappe.flags.mute_emails:
		return
	invoices = [
		ref.reference_name
		for ref in doc.references
		if ref.reference_doctype == "Sales Invoice" and ref.allocated_amount
	]
	if not invoices or not frappe.get_all(
		"Sales Invoice", filters={"name": ["in", invoices], "lease": ["is", "set"]}, limit=1
	):
		return
	frappe.enqueue(
		"skyeng_immo.sky_immo.notifications.send_payment_emails",
		payment_entry=doc.name,
		enqueue_after_commit=True,
	)


def send_payment_emails(payment_entry: str):
	pe = frappe.get_doc("Payment Entry", payment_entry)
	allocated = {
		ref.reference_name: ref.allocated_amount
		for ref in pe.references
		if ref.reference_doctype == "Sales Invoice" and ref.allocated_amount
	}
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"name": ["in", list(allocated) or [""]], "lease": ["is", "set"]},
		fields=["name", "customer", "customer_name", "lease", "currency"],
		ignore_permissions=True,
	)
	if not invoices:
		return
	currency = invoices[0].currency or pe.paid_from_account_currency
	for invoice in invoices:
		invoice.property = frappe.db.get_value("Lease", invoice.lease, "property")

	def context_for(group):
		def context(lang):
			return {
				"amount": _money(sum(allocated[invoice.name] for invoice in group), currency),
				"date": formatdate(pe.posting_date),
				"property": ", ".join(sorted({_property_label(i.property) for i in group if i.property})),
				"invoices": ", ".join(invoice.name for invoice in group),
				"tenant": invoices[0].customer_name or invoices[0].customer,
				"app_url": get_url(APP_ROUTE),
			}

		return context

	def receipt(lang):
		# Rendered by the email queue when it sends (frappe.attach_print): a raw PDF
		# passed here would be dropped, the queue only keeps files and print formats.
		return [
			{
				"print_format_attachment": 1,
				"doctype": "Payment Entry",
				"name": pe.name,
				"file_name": pe.name,
				"lang": lang,
			}
		]

	reference = ("Payment Entry", pe.name)
	send("Receipt", tenant_recipients(invoices[0].customer), context_for(invoices), reference, attach=receipt)

	# One notice per landlord, about their own invoices only: a tenant renting from two
	# landlords may settle both in one payment, and neither may learn about the other.
	by_owner: dict = {}
	for invoice in invoices:
		by_owner.setdefault(owner_of(invoice.property), []).append(invoice)
	for group in by_owner.values():
		send("Payment notice", landlord_recipients(group[0].property), context_for(group), reference)


def send_due_reminders():
	"""Daily job: remind tenants of rent invoices falling due in REMINDER_DAYS days."""
	target = add_days(today(), REMINDER_DAYS)
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"is_return": 0,
			"lease": ["is", "set"],
			"outstanding_amount": [">", 0],
			"due_date": target,
		},
		fields=[
			"name",
			"customer",
			"lease",
			"due_date",
			"from_date",
			"to_date",
			"outstanding_amount",
			"currency",
		],
		ignore_permissions=True,
	)
	for invoice in invoices:
		property_name = frappe.db.get_value("Lease", invoice.lease, "property")

		def context(lang, invoice=invoice, property_name=property_name):
			period = (
				f"{formatdate(invoice.from_date)} – {formatdate(invoice.to_date)}"
				if invoice.from_date and invoice.to_date
				else ""
			)
			return {
				"amount": _money(invoice.outstanding_amount, invoice.currency),
				"due_date": formatdate(getdate(invoice.due_date)),
				"property": _property_label(property_name),
				"period": period,
				"invoice": invoice.name,
				"app_url": get_url(APP_ROUTE),
			}

		try:
			send(
				"Due reminder", tenant_recipients(invoice.customer), context, ("Sales Invoice", invoice.name)
			)
		except Exception:
			frappe.log_error(f"Sky Immo: due reminder for {invoice.name}")
