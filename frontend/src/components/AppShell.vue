<template>
  <div class="min-h-screen md:flex">
    <!-- desktop sidebar, folds to an icon rail (tablets start folded so the page keeps its room) -->
    <aside class="sticky top-0 hidden h-screen shrink-0 flex-col border-r border-line bg-card transition-[width] duration-200 md:flex"
      :class="folded ? 'w-[76px]' : 'w-[248px]'">
      <div class="flex items-center pb-6 pt-6" :class="folded ? 'flex-col gap-3 px-3' : 'justify-between pl-6 pr-3'">
        <RouterLink :to="home()" :aria-label="t('Home')"><Logo :mark-only="folded" :subtitle="t(spaceLabel)" /></RouterLink>
        <button class="flex size-8 items-center justify-center rounded-full text-ink-mute transition hover:bg-paper hover:text-ink"
          :title="folded ? t('Expand menu') : t('Collapse menu')" :aria-label="folded ? t('Expand menu') : t('Collapse menu')" @click="toggleFold">
          <span :class="folded ? 'lucide-panel-left-open' : 'lucide-panel-left-close'" class="size-[17px]" />
        </button>
      </div>

      <nav class="flex-1 overflow-y-auto px-3" :aria-label="t('Main menu')">
        <p v-if="!folded" class="eyebrow mb-2 px-3">{{ t('Menu') }}</p>
        <RouterLink v-for="item in items" :key="item.to" :to="item.to" :title="folded ? t(item.label) : undefined"
          class="group relative mb-0.5 flex items-center gap-3 rounded-[12px] py-2.5 text-[14px] transition"
          :class="[folded ? 'justify-center px-0' : 'px-3',
            isActive(item, route.path) ? 'bg-sky-soft font-semibold text-sky' : 'font-medium text-ink-soft hover:bg-paper hover:text-ink']"
          :aria-current="isActive(item, route.path) ? 'page' : undefined">
          <span :class="[item.icon, isActive(item, route.path) ? 'text-sky-mid' : 'text-ink-mute group-hover:text-ink-soft']" class="size-[18px] shrink-0" />
          <span v-if="!folded" class="flex-1">{{ t(item.label) }}</span>
          <span v-if="badge(item) && !folded" class="rounded-full bg-warn px-1.5 py-px text-[11px] font-semibold text-white tabular">{{ badge(item) }}</span>
          <span v-else-if="badge(item)" class="absolute right-3 top-2 size-2 rounded-full bg-warn ring-2 ring-card" />
        </RouterLink>
      </nav>

      <div class="p-3">
        <div v-if="!folded && space() === 'tenant'" class="mb-3 rounded-[16px] bg-sky-mist p-4">
          <p class="font-display text-[17px] leading-snug text-sky">{{ t('Something broken at home?') }}</p>
          <p class="mt-1 text-[12.5px] leading-snug text-ink-mute">{{ t('Tell us in a minute, with a photo.') }}</p>
          <Btn class="mt-3" variant="brand" size="sm" icon="lucide-plus" :label="t('Report a problem')" to="/locataire/maintenance/nouvelle" />
        </div>
        <Dropdown :options="userMenu" side="top" align="start">
          <template #default>
            <button class="flex w-full items-center gap-3 rounded-[12px] p-2 text-left transition hover:bg-paper" :class="folded && 'justify-center'">
              <Initials :name="session.user.fullName" />
              <template v-if="!folded">
                <div class="min-w-0 flex-1">
                  <div class="truncate text-[13.5px] font-semibold text-ink">{{ session.user.fullName }}</div>
                  <div class="truncate text-[12px] text-ink-mute">{{ t(roleLabel) }}</div>
                </div>
                <span class="lucide-chevrons-up-down size-4 text-ink-faint" />
              </template>
            </button>
          </template>
        </Dropdown>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <!-- top bar -->
      <header class="sticky top-0 z-20 flex h-[60px] items-center gap-2 bg-paper/85 px-4 backdrop-blur-md md:h-16 md:px-8 lg:px-10">
        <RouterLink :to="home()" class="md:hidden" :aria-label="t('Home')"><Logo mark-class="size-9" /></RouterLink>
        <div class="flex-1" />
        <div class="hidden items-center rounded-full border border-line bg-card p-0.5 sm:flex" role="group" :aria-label="t('Language')">
          <button v-for="l in ['fr', 'en']" :key="l" class="rounded-full px-2.5 py-1 text-[11.5px] font-semibold uppercase tracking-wide transition"
            :class="lang === l ? 'bg-ink text-on-ink' : 'text-ink-mute hover:text-ink'" :aria-pressed="lang === l" @click="changeLanguage(l)">{{ l }}</button>
        </div>
        <button class="hidden size-10 items-center justify-center rounded-full border border-line bg-card text-ink-soft shadow-card transition hover:text-ink sm:flex"
          :title="isDark ? t('Light theme') : t('Dark theme')" :aria-label="isDark ? t('Light theme') : t('Dark theme')"
          @click="setTheme(isDark ? 'light' : 'dark')">
          <span :class="isDark ? 'lucide-sun' : 'lucide-moon'" class="size-[17px]" />
        </button>
        <div class="md:hidden">
          <Dropdown :options="userMenu" align="end">
            <template #default>
              <button class="rounded-full" :aria-label="t('My account')"><Initials :name="session.user.fullName" /></button>
            </template>
          </Dropdown>
        </div>
      </header>

      <ConnectionBanner />
      <InstallBanner />

      <main class="mx-auto w-full min-w-0 max-w-[1200px] flex-1 px-4 pb-32 pt-3 md:px-8 md:pb-14 md:pt-5 lg:px-10">
        <slot />
      </main>
    </div>

    <!-- phone tab bar -->
    <nav class="fixed inset-x-3 bottom-[max(12px,env(safe-area-inset-bottom))] z-30 mx-auto max-w-[480px] md:hidden" :aria-label="t('Main menu')">
      <div class="grid items-center rounded-[24px] border border-line bg-card/95 px-1 py-1 shadow-lift backdrop-blur" :style="{ gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` }">
        <RouterLink v-for="item in items" :key="item.to" :to="item.to"
          class="relative flex min-w-0 flex-col items-center gap-0.5 py-1.5"
          :class="isActive(item, route.path) ? 'text-ink' : 'text-ink-mute'" :aria-current="isActive(item, route.path) ? 'page' : undefined">
          <span :class="item.icon" class="size-[19px]" />
          <span class="w-full truncate text-center text-[10.5px] font-semibold">{{ t(item.short) }}</span>
          <span v-if="isActive(item, route.path)" class="absolute -bottom-0.5 h-[3px] w-4 rounded-full bg-sky-mid" />
          <span v-if="badge(item)" class="absolute right-[24%] top-1 size-2 rounded-full bg-warn ring-2 ring-card" />
        </RouterLink>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useMediaQuery } from '@vueuse/core'
import { Dropdown } from 'frappe-ui'
import Logo from './Logo.vue'
import Btn from './Btn.vue'
import Initials from './Initials.vue'
import ConnectionBanner from './ConnectionBanner.vue'
import InstallBanner from './InstallBanner.vue'
import { post } from '@/api'
import { lang, setLanguage, t } from '@/i18n'
import { isDark, setTheme } from '@/theme'
import { session, logout, space, spaces, home, switchSpace } from '@/session'
import { ownerNav, tenantNav, isActive } from '@/nav'
import { loadAttention, awaitingCount } from '@/attention'

const route = useRoute()
loadAttention()
const badge = (item) => (item.badge === 'awaiting' ? awaitingCount() : 0)
const items = computed(() => (space() === 'tenant' ? tenantNav : ownerNav))
// The open space decides: someone both landlord and tenant reads "Tenant" in their tenant space.
const roleLabel = computed(() => (space() === 'tenant' ? 'Tenant' : session.user.role === 'manager' ? 'Property manager' : 'Landlord'))
const spaceLabel = computed(() => (space() === 'tenant' ? 'Tenant space' : 'Landlord space'))

const tablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)')
const read = (k, d) => {
  try {
    return localStorage.getItem(k) ?? d
  } catch {
    return d
  }
}
const deskFolded = ref(read('sky_immo.sidebar', 'open') === 'folded')
const tabletFolded = ref(read('sky_immo.sidebar.tablet', 'folded') === 'folded')
const folded = computed(() => (tablet.value ? tabletFolded.value : deskFolded.value))
function toggleFold() {
  const target = tablet.value ? tabletFolded : deskFolded
  target.value = !target.value
  try {
    localStorage.setItem(tablet.value ? 'sky_immo.sidebar.tablet' : 'sky_immo.sidebar', target.value ? 'folded' : 'open')
  } catch {}
}

// saved on the account too, so emails go out in the same language
function changeLanguage(l) {
  setLanguage(l)
  post('set_language', { lang: l }).catch(() => {})
}

const otherSpace = computed(() => spaces().find((s) => s !== space()))
const userMenu = computed(() => [
  { label: t('My account'), icon: 'lucide-user-round', route: { path: `${home()}/compte` } },
  ...(otherSpace.value
    ? [{ label: otherSpace.value === 'tenant' ? t('Open my tenant space') : t('Open my landlord space'), icon: 'lucide-arrow-left-right', onClick: () => switchSpace(otherSpace.value) }]
    : []),
  { label: isDark.value ? t('Light theme') : t('Dark theme'), icon: isDark.value ? 'lucide-sun' : 'lucide-moon', onClick: () => setTheme(isDark.value ? 'light' : 'dark') },
  { label: lang.value === 'fr' ? 'English' : 'Français', icon: 'lucide-languages', onClick: () => changeLanguage(lang.value === 'fr' ? 'en' : 'fr') },
  { label: t('Sign out'), icon: 'lucide-log-out', theme: 'red', onClick: logout },
])
</script>
