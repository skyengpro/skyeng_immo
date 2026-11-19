let messages = {};

export function __(message, replacements = []) {
	const translated = messages[message] || message;
	return translated.replace(/{(\d+)}/g, (match, index) => replacements[index] ?? match);
}

// Loads the site's translations for the signed-in user's language before the app mounts.
export async function loadTranslations() {
	try {
		const response = await fetch("/api/method/skyeng_immo.api.get_translations", {
			headers: { Accept: "application/json" },
		});
		if (response.ok) {
			messages = (await response.json()).message || {};
		}
	} catch {
		messages = {};
	}
}

export const translationPlugin = {
	install(app) {
		app.config.globalProperties.__ = __;
	},
};
