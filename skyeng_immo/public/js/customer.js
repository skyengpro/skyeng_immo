const INVITER_ROLES = ["System Manager", "Property Manager"];

frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.is_new() || !INVITER_ROLES.some((role) => frappe.user.has_role(role))) {
			return;
		}
		frm.add_custom_button(__("Invite to Sky-immo"), () => {
			frappe.confirm(__("Send an invitation to {0}?", [frm.doc.customer_name]), () => {
				frappe.call({
					method: "skyeng_immo.invitation.invite_customer",
					args: { customer: frm.doc.name },
					freeze: true,
					callback: ({ message }) => {
						frappe.show_alert({
							message: __("Invitation sent to {0}", [message.user]),
							indicator: "green",
						});
						frm.reload_doc();
					},
				});
			});
		});
	},
});
