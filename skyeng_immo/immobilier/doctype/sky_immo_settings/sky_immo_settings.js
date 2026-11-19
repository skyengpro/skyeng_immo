// Grey help text shown under Operating mode, one per option.
const OPERATING_MODE_DESCRIPTIONS = {
	"Sky owns an instance": __("We own the instance"),
	"A customer owns an instance": __("A customer owns this instance"),
};

frappe.ui.form.on("Sky Immo Settings", {
	refresh(frm) {
		frm.trigger("set_operating_mode_description");
	},

	operating_mode(frm) {
		frm.trigger("set_operating_mode_description");
	},

	set_operating_mode_description(frm) {
		const description = OPERATING_MODE_DESCRIPTIONS[frm.doc.operating_mode] || "";
		frm.set_df_property("operating_mode", "description", description);
	},
});
