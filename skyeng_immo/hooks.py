app_name = "skyeng_immo"
app_title = "SkyEng Immo"
app_publisher = "SkyEngPro"
app_description = "Gestion immobiliere - occupants, visiteurs, vehicules, parking"
app_email = "contact@skyengpro.com"
app_license = "MIT"

# Occupant, Visitor Log, Vehicle and Parking Space all link to PropMS
# `Property` / `Lease`, and the equipment layer extends ERPNext `Asset`.
# Declaring these makes `install-app` refuse up front on a bare site instead
# of failing halfway through doctype sync.
required_apps = ["erpnext", "propms"]

# Roles and the Asset custom fields (warranty, unit link) are created in code
# rather than left as site data: a fresh install must yield a working app,
# not four DocTypes whose permissions point at roles that do not exist.
after_install = "skyeng_immo.install.after_install"
after_migrate = "skyeng_immo.install.after_migrate"

# --------------------------------------------------------------------------- #
# Sky Immo: the landlord and tenant app (doc/EP-01-landlord-tenant-app.md)    #
# --------------------------------------------------------------------------- #

# The Vue app (frontend/, frappe-ui) is built into public/frontend and served as the page
# www/sky-immo.html; every deep link falls back to that page. It is a PWA: its service worker is
# re-served from /sky-immo/sw.js so it controls the whole /sky-immo scope.
website_route_rules = [
	{"from_route": "/sky-immo/<path:app_path>", "to_route": "sky-immo"},
]
page_renderer = ["skyeng_immo.sky_immo.service_worker.ServiceWorkerPage"]

# The app used to live at /mon-immo: keep old links and bookmarks working.
website_redirects = [
	{"source": r"/mon-immo(/.*)?", "target": r"/sky-immo\1"},
]

# After the invitation's "set your password" step (and after sign-in), Frappe
# sends website users to their role's home page: the app.
role_home_page = {"Landlord": "sky-immo", "Tenant": "sky-immo"}

# Icon on the desk's apps screen and in the sidebar app switcher, for staff, landlords
# and tenants (see access.has_app_permission).
add_to_apps_screen = [
	{
		"name": "skyeng_immo",
		"logo": "/assets/skyeng_immo/frontend/logo-mark.svg",
		"title": "Sky Immo",
		"route": "/sky-immo",
		"has_permission": "skyeng_immo.sky_immo.access.has_app_permission",
	}
]

# "Give access to the app" button on the Customer form.
doctype_js = {
	"Customer": "public/js/customer_sky_immo.js",
	"Issue": "public/js/issue_sky_immo.js",
}

doc_events = {
	"User": {"validate": "skyeng_immo.sky_immo.access.set_default_app"},
	"Property": {"validate": "skyeng_immo.sky_immo.validation.validate_property"},
	"Lease": {"validate": "skyeng_immo.sky_immo.validation.validate_lease"},
	"Issue": {"on_update": "skyeng_immo.sky_immo.maintenance.on_issue_update"},
	"Payment Entry": {"on_submit": "skyeng_immo.sky_immo.notifications.on_payment_entry_submit"},
}

scheduler_events = {
	"daily": ["skyeng_immo.sky_immo.notifications.send_due_reminders"],
}

# Fixtures ship the dashboard so a fresh install brings the whole thing, not
# just empty DocTypes. Order matters: cards, charts and reports must exist
# before the Workspace that references them.
#
# Each entry is an explicit allowlist. A broad filter (is_public = 1) would
# sweep in ERPNext's ~50 built-in cards and charts and make this app own and
# overwrite them on every migrate.
fixtures = [
	{
		"dt": "Number Card",
		"filters": [
			[
				"name",
				"in",
				[
					"Unites totales",
					"Unites louees",
					"Unites libres",
					"Baux actifs",
					"Occupants actifs",
					"Visiteurs presents",
					"Visites (total)",
					"Facture (XAF)",
					"Encaisse (XAF)",
					"Impayes (XAF)",
					"Factures impayees",
					"Cautions detenues (XAF)",
					"Compteurs actifs",
					"Controles maintenance",
					"Polices d'assurance",
					"Equipements",
					"Hors garantie",
				],
			]
		],
	},
	{
		"dt": "Dashboard Chart",
		"filters": [
			[
				"name",
				"in",
				[
					"Statut des unites",
					"Unites par immeuble",
					"Loyer par immeuble (XAF)",
					"Facturation prevue (XAF)",
					"Facturation par mois (XAF)",
					"Encaissements par mois (XAF)",
					"Visites par motif",
				],
			]
		],
	},
	{"dt": "Report", "filters": [["module", "=", "Immobilier"], ["is_standard", "=", "No"]]},
	{"dt": "Custom Field", "filters": [["name", "in", ["Issue-sky_immo_status"]]]},
	{"dt": "Workspace", "filters": [["name", "=", "Immobilier"]]},
	{"dt": "Workspace Sidebar", "filters": [["name", "=", "Immobilier"]]},
	{"dt": "Desktop Icon", "filters": [["label", "=", "Immobilier"]]},
]
