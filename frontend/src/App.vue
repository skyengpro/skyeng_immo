<template>
  <FrappeUIProvider>
    <RouterView v-if="route.meta.public" />
    <AppShell v-else-if="session.user">
      <RouterView v-slot="{ Component }">
        <component :is="Component" :key="route.path" />
      </RouterView>
    </AppShell>
    <div v-else class="flex h-screen items-center justify-center">
      <LoadingIndicator class="size-6 text-ink-mute" />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { FrappeUIProvider, LoadingIndicator } from 'frappe-ui'
import AppShell from './components/AppShell.vue'
import { session } from './session'
import { t } from './i18n'

const route = useRoute()
watchEffect(() => {
  document.title = route.meta.title ? `${t(route.meta.title)} · Sky-immo` : 'Sky-immo'
})
</script>
