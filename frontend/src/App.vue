<template>
	<div class="flex min-h-screen min-w-0 flex-col bg-surface-gray-1 text-ink-gray-9">
		<header
			class="sticky top-0 z-10 border-b border-outline-gray-1 bg-surface-white pt-[env(safe-area-inset-top)]"
		>
			<div class="mx-auto flex h-14 w-full max-w-5xl items-center justify-between gap-3 px-4">
				<span class="truncate text-lg font-semibold">Sky-immo</span>
				<Button variant="ghost" size="md" :label="__('Sign out')" @click="signOut" />
			</div>
		</header>
		<main class="mx-auto w-full min-w-0 max-w-5xl flex-1 px-4 py-6 pb-[max(1.5rem,env(safe-area-inset-bottom))]">
			<router-view />
		</main>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui";

async function signOut() {
	await fetch("/api/method/logout", {
		method: "POST",
		headers: { "X-Frappe-CSRF-Token": window.csrf_token || "" },
	});
	window.location.href = "/login?redirect-to=/sky-immo";
}
</script>
