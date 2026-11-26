<template>
  <div>
    <PageHeader :eyebrow="t('Settings')" :title="t('My account')" />
    <div class="grid grid-cols-[minmax(0,1fr)] gap-4 md:max-w-3xl md:grid-cols-2 md:gap-5">
      <Panel :title="t('Profile')" padded class="md:col-span-2">
        <div class="mb-4 flex items-center gap-4">
          <Initials :name="session.user.fullName" size="xl" />
          <div class="min-w-0">
            <p class="truncate font-display text-[24px] text-ink">{{ session.user.fullName }}</p>
            <p class="text-[13px] text-ink-mute">{{ t(roleLabel) }}</p>
          </div>
        </div>
        <Facts :items="[{ label: t('Email'), value: session.user.email }, { label: t('Space'), value: t(roleLabel) }]" />
      </Panel>

      <Panel v-if="spaces().length > 1" :title="t('Space')" padded class="md:col-span-2">
        <div class="flex items-center rounded-full border border-line bg-paper p-0.5" role="group" :aria-label="t('Space')">
          <button v-for="o in [['owner', 'Landlord'], ['tenant', 'Tenant']]" :key="o[0]" class="flex-1 rounded-full py-2 text-[13.5px] font-semibold transition"
            :class="space() === o[0] ? 'bg-ink text-on-ink' : 'text-ink-mute hover:text-ink'" :aria-pressed="space() === o[0]" @click="switchSpace(o[0])">{{ t(o[1]) }}</button>
        </div>
        <p class="mt-3 text-[12.5px] text-ink-mute">{{ t('You are both landlord and tenant: switch between your properties and your own lease.') }}</p>
      </Panel>

      <Panel :title="t('Language')" padded>
        <div class="flex items-center rounded-full border border-line bg-paper p-0.5" role="group" :aria-label="t('Language')">
          <button v-for="o in [['fr', 'Français'], ['en', 'English']]" :key="o[0]" class="flex-1 rounded-full py-2 text-[13.5px] font-semibold transition"
            :class="lang === o[0] ? 'bg-ink text-on-ink' : 'text-ink-mute hover:text-ink'" :aria-pressed="lang === o[0]" @click="change(o[0])">{{ o[1] }}</button>
        </div>
        <p class="mt-3 text-[12.5px] text-ink-mute">{{ t('Screens, and the emails you receive, switch to this language.') }}</p>
      </Panel>

      <Panel :title="t('Appearance')" padded>
        <div class="flex items-center rounded-full border border-line bg-paper p-0.5" role="group" :aria-label="t('Appearance')">
          <button v-for="o in modes" :key="o[0]" class="flex flex-1 items-center justify-center gap-1.5 rounded-full py-2 text-[13.5px] font-semibold transition"
            :class="themeMode === o[0] ? 'bg-ink text-on-ink' : 'text-ink-mute hover:text-ink'" :aria-pressed="themeMode === o[0]" @click="setTheme(o[0])">
            <span :class="o[2]" class="size-4" />{{ t(o[1]) }}
          </button>
        </div>
        <p class="mt-3 text-[12.5px] text-ink-mute">{{ t('Light, dark, or the same as your phone.') }}</p>
      </Panel>

      <p class="flex items-start gap-3 rounded-[16px] border border-line bg-card/60 px-4 py-3.5 text-[13.5px] text-ink-soft md:col-span-2">
        <span class="lucide-info mt-0.5 size-4 shrink-0 text-sky-mid" />
        {{ session.user.role === 'manager' ? t('Staff manage leases, tenants and payments in the desk.') : t('To change any information (lease, contact details, payment), contact your property manager.') }}
      </p>

      <div class="md:col-span-2"><Btn icon="lucide-log-out" :label="t('Sign out')" @click="logout" /></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Panel from '@/components/Panel.vue'
import Facts from '@/components/Facts.vue'
import Btn from '@/components/Btn.vue'
import Initials from '@/components/Initials.vue'
import { post } from '@/api'
import { lang, setLanguage, t } from '@/i18n'
import { setTheme, themeMode } from '@/theme'
import { session, logout, space, spaces, switchSpace } from '@/session'

// The open space decides: someone both landlord and tenant reads "Tenant" in their tenant space.
const roleLabel = computed(() => (space() === 'tenant' ? 'Tenant' : session.user.role === 'manager' ? 'Property manager' : 'Landlord'))
const modes = [['light', 'Light', 'lucide-sun'], ['system', 'Auto', 'lucide-monitor-smartphone'], ['dark', 'Dark', 'lucide-moon']]
function change(l) {
  setLanguage(l)
  post('set_language', { lang: l }).catch(() => {})
}
</script>
