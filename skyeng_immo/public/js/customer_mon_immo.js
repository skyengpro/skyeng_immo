// Customer form: give the landlord or the tenant access to the Mon Immo app.
// Creates the account, links it to this Customer (Portal Users) and sends the invitation email.
frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (!frappe.user.has_role("System Manager") && !frappe.user.has_role("Property Manager")) return;

		frm.add_custom_button(__("Mon Immo access"), () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Give access to the Mon Immo app"),
				fields: [
					{
						fieldname: "role",
						fieldtype: "Select",
						label: __("This customer is"),
						options: [
							{ value: "Tenant", label: __("A tenant") },
							{ value: "Landlord", label: __("A landlord") },
						],
						default: "Tenant",
						reqd: 1,
					},
					{
						fieldname: "email",
						fieldtype: "Data",
						options: "Email",
						label: __("Email"),
						default: frm.doc.email_id,
						reqd: 1,
					},
					{
						fieldname: "language",
						fieldtype: "Select",
						label: __("Language of the app and emails"),
						options: [
							{ value: "fr", label: "Français" },
							{ value: "en", label: "English" },
						],
						default: "fr",
					},
					{
						fieldtype: "HTML",
						options: `<p class="text-muted small">${__(
							"An invitation email lets the person choose a password, then opens the app.",
						)}</p>`,
					},
				],
				primary_action_label: __("Send the invitation"),
				primary_action(values) {
					frappe.call({
						method: "skyeng_immo.mon_immo.invite.invite_to_app",
						args: { customer: frm.doc.name, ...values },
						freeze: true,
						callback({ message }) {
							dialog.hide();
							if (message.emailError) {
								frappe.msgprint({ title: __("Invitation not sent"), indicator: "orange", message: message.emailError });
							} else {
								frappe.show_alert({
									indicator: "green",
									message: message.invitationSent
										? __("Invitation sent to {0}", [message.user])
										: __("{0} already uses the app. Access updated.", [message.user]),
								});
							}
							frm.reload_doc();
						},
					});
				},
			});
			dialog.show();
		});
	},
});
