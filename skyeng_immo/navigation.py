"""Where each user goes: the apps-screen tile, the landing page and the default app."""

import frappe

from skyeng_immo.access import LANDLORD, TENANT, is_manager
from skyeng_immo.immobilier.doctype.sky_immo_settings.sky_immo_settings import (
	MODE_CUSTOMER,
	get_operating_mode,
)

APP_NAME = "skyeng_immo"
APP_ROLES = frozenset({LANDLORD, TENANT})


def has_app_permission() -> bool:
	"""Tile visibility: landlords and tenants, and managers where the customer runs the site."""
	user = frappe.session.user
	if user == "Guest":
		return False
	if is_manager(user):
		return get_operating_mode() == MODE_CUSTOMER
	return not APP_ROLES.isdisjoint(frappe.get_roles(user))


def get_home_page(user: str) -> str | None:
	"""Landing page of a manager on a customer-owned site; None leaves Frappe's choice."""
	if is_manager(user) and get_operating_mode() == MODE_CUSTOMER:
		return "sky-immo"


def set_default_app(doc, method=None) -> None:
	"""Make the app the default of a Website User holding Landlord or Tenant, unless they chose one.

	Frappe sends a Website User to their default app after sign-in; without it they would
	land on PropMS's Desk route, which the apps screen offers to every signed-in user.
	"""
	roles = {row.role for row in doc.get("roles")}
	if doc.user_type == "Website User" and not doc.default_app and not APP_ROLES.isdisjoint(roles):
		doc.default_app = APP_NAME
