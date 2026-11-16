import path from "node:path";

import vue from "@vitejs/plugin-vue";
import frappeui from "frappe-ui/vite";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			lucideIcons: false,
			jinjaBootData: true,
			buildConfig: {
				outDir: "../skyeng_immo/public/frontend",
				baseUrl: "/assets/skyeng_immo/frontend/",
				indexHtmlPath: "../skyeng_immo/www/sky_immo.html",
				emptyOutDir: true,
			},
		}),
		vue(),
	],
	resolve: {
		alias: { "@": path.resolve(import.meta.dirname, "src") },
	},
	server: {
		allowedHosts: true,
	},
});
