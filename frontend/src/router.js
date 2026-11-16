import { createRouter, createWebHistory } from "vue-router";

import Home from "@/pages/Home.vue";

const routes = [
	{ path: "/", name: "Home", component: Home },
	{ path: "/:pathMatch(.*)*", redirect: { name: "Home" } },
];

export default createRouter({
	history: createWebHistory("/sky-immo"),
	routes,
});
