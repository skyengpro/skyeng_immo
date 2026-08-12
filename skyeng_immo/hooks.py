app_name = "skyeng_immo"
app_title = "SkyEng Immo"
app_publisher = "SkyEngPro"
app_description = "Gestion immobiliere - occupants, visiteurs, vehicules, parking"
app_email = "contact@skyengpro.com"
app_license = "MIT"

# Occupant and Visitor Log both link to PropMS `Property` / `Lease`, and the
# billing side lives in ERPNext. Declaring these makes `install-app` refuse
# up front on a bare site instead of failing halfway through doctype sync.
required_apps = ["erpnext", "propms"]
