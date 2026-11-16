import "./index.css";

import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";
import { loadTranslations, translationPlugin } from "./translation";

loadTranslations().then(() => {
	createApp(App).use(router).use(translationPlugin).mount("#app");
});
