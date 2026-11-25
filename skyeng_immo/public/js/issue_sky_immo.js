// Issue form: the owner of the property approves or rejects a tenant's maintenance request.
// The buttons show only to a user linked to the owner, while the request awaits a decision.
frappe.ui.form.on("Issue", {
	async refresh(frm) {
		if (frm.is_new() || frm.doc.sky_immo_status !== "Awaiting approval") return;

		const { message } = await frappe.call({
			method: "skyeng_immo.sky_immo.maintenance.desk_permissions",
			args: { name: frm.doc.name },
		});
		if (!message || !message.canDecide) return;

		const decide = (decision, confirmation) => {
			frappe.confirm(confirmation, async () => {
				await frappe.call({
					method: "skyeng_immo.sky_immo.maintenance.decide",
					args: { name: frm.doc.name, decision },
					freeze: true,
				});
				frm.reload_doc();
			});
		};

		frm.add_custom_button(__("Approve"), () => decide("approve", __("Approve this request?")), __("Decision"));
		frm.add_custom_button(__("Reject"), () => decide("reject", __("Reject this request?")), __("Decision"));
		frm.page.set_inner_btn_group_as_primary(__("Decision"));
	},
});
