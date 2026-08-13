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
