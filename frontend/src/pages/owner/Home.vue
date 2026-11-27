<template>
  <div>
    <div class="rise mb-8 flex flex-wrap items-end justify-between gap-5">
      <div>
        <p class="eyebrow mb-2">{{ longDate(new Date()) }}</p>
        <h1 class="font-display text-[30px] leading-[1.08] text-ink md:text-[44px]">{{ greeting }}, <em class="italic text-sky-mid">{{ session.user.firstName }}</em></h1>
        <p v-if="data" class="mt-2 text-[14px] text-ink-mute md:text-[15px]">{{ summary }}</p>
      </div>
      <div class="grid w-full grid-cols-2 gap-2 sm:flex sm:w-auto">
        <Btn icon="lucide-wrench" :label="t('Repairs')" to="/proprietaire/maintenance" />
        <Btn variant="primary" icon="lucide-building-2" :label="t('My properties')" to="/proprietaire/biens" />
      </div>
    </div>

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" stats :rows="2" />
    <template v-else>
      <div class="grid grid-cols-2 gap-3 md:gap-4 lg:grid-cols-4">
        <StatCard :label="t('Properties')" :value="num(data.stats.properties)" icon="lucide-building-2" to="/proprietaire/biens" />
        <StatCard :label="t('Tenants')" :value="num(data.stats.tenants)" icon="lucide-users-round" to="/proprietaire/locataires" />
        <StatCard :label="t('Received this month')" :value="money(data.stats.collectedThisMonth)" icon="lucide-wallet" tone="ok" small />
        <StatCard :label="t('Still to collect')" :value="money(data.stats.unpaidTotal)" icon="lucide-circle-alert" small
          :tone="data.stats.unpaidTotal ? 'red' : 'ok'" :hint-tone="data.stats.unpaidTotal ? 'red' : null"
          :hint="tn(data.stats.unpaidCount, '{0} invoice', '{0} invoices')" />
      </div>

      <!-- phone: occupancy right under the four figures -->
      <OccupancyCard v-if="occupancy.total" class="mt-3 md:hidden" :occupancy="occupancy" />

      <!-- phone: one list at a time, picked with side-by-side buttons; wider screens show all three -->
      <Tabs v-model="pick" cards class="mt-6 md:hidden" :label="t('What needs attention')" :options="picks" />

      <div class="mt-4 grid grid-cols-[minmax(0,1fr)] gap-4 md:mt-8 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)] lg:gap-5">
        <Panel :class="pick !== 'late' && 'max-md:hidden'" :title="t('Late invoices')" :count="data.overdue.length || null">
          <EmptyState v-if="!data.overdue.length" icon="lucide-circle-check" :title="t('Nothing is late')" :text="t('Every invoice is paid or not due yet.')" />
          <ul v-else class="stagger divide-y divide-line">
            <Row v-for="inv in data.overdue" :key="inv.id" :to="inv.leaseId ? `/proprietaire/baux/${encodeURIComponent(inv.leaseId)}` : `/proprietaire/factures/${encodeURIComponent(inv.id)}`">
              <template #lead><Initials :name="inv.tenant.name" /></template>
              <p class="truncate text-[14.5px] font-semibold text-ink">{{ inv.tenant.name }}</p>
              <p class="truncate text-[12.5px] text-ink-mute">{{ inv.property?.displayName }}</p>
              <template #end>
                <span class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ money(inv.outstanding) }}</span>
                <span class="rounded-full bg-alert-soft px-2 py-0.5 text-[11.5px] font-medium text-alert">{{ tn(inv.daysLate, 'Late by {0} day', 'Late by {0} days') }}</span>
              </template>
            </Row>
          </ul>
        </Panel>

        <div class="space-y-4 lg:space-y-5">
          <Panel :class="pick !== 'awaiting' && 'max-md:hidden'" :title="t('Maintenance requests')" :count="awaiting.length || null">
            <template v-if="awaiting.length" #actions>
              <RouterLink to="/proprietaire/maintenance" class="text-[12.5px] font-semibold text-sky-mid hover:underline">{{ t('See all') }}</RouterLink>
            </template>
            <p v-if="!awaiting.length" class="flex items-center gap-2 px-5 pb-5 text-[13.5px] text-ink-mute">
              <span class="lucide-circle-check size-4 text-ok" />{{ t('No repair waits for you.') }}
            </p>
            <IssueList v-else :issues="awaiting.slice(0, 4)" base="/proprietaire" show-tenant class="!rounded-none !border-0 !shadow-none" />
          </Panel>

          <Panel :class="pick !== 'progress' && 'max-md:hidden'" :title="t('Maintenance in progress')" :count="inProgress.length || null">
            <template v-if="inProgress.length" #actions>
              <RouterLink to="/proprietaire/maintenance" class="text-[12.5px] font-semibold text-sky-mid hover:underline">{{ t('See all') }}</RouterLink>
            </template>
            <p v-if="!inProgress.length" class="flex items-center gap-2 px-5 pb-5 text-[13.5px] text-ink-mute">
              <span class="lucide-circle-check size-4 text-ok" />{{ t('No repair in progress.') }}
            </p>
            <IssueList v-else :issues="inProgress.slice(0, 4)" base="/proprietaire" show-tenant class="!rounded-none !border-0 !shadow-none" />
          </Panel>

          <OccupancyCard v-if="occupancy.total" class="hidden md:block" :occupancy="occupancy" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Btn from '@/components/Btn.vue'
import Tabs from '@/components/Tabs.vue'
import OccupancyCard from '@/components/OccupancyCard.vue'
import StatCard from '@/components/StatCard.vue'
import Panel from '@/components/Panel.vue'
import Row from '@/components/Row.vue'
import Initials from '@/components/Initials.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import IssueList from '@/components/IssueList.vue'
import { get } from '@/api'
import { attention } from '@/attention'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { longDate, money, num } from '@/format'
import { session } from '@/session'

const { data, error, reload } = useLoad('get_owner_dashboard')
const units = ref([])
get('list_properties').then((list) => (units.value = list.sections.flatMap((s) => s.groups.flatMap((g) => g.units)))).catch(() => {})
const awaiting = computed(() => attention.issues.filter((i) => i.approval === 'awaiting_approval'))
const inProgress = computed(() => attention.issues.filter((i) => i.approval === 'in_progress'))
// phone: the list shown under the buttons. Until one is tapped, the first that has something in it
const picked = ref('')
const picks = computed(() => [
  { value: 'late', label: t('Late invoices'), icon: 'lucide-receipt-text', count: data.value?.overdue.length, tone: 'red' },
  { value: 'awaiting', label: t('Maintenance requests'), icon: 'lucide-wrench', count: awaiting.value.length, tone: 'red' },
  { value: 'progress', label: t('Maintenance in progress'), icon: 'lucide-hammer', count: inProgress.value.length },
])
const pick = computed({
  get: () => picked.value || picks.value.find((p) => p.count)?.value || 'late',
  set: (value) => (picked.value = value),
})
const occupancy = computed(() => {
  const total = units.value.length
  const count = (st) => units.value.filter((u) => u.status === st).length
  const let_ = count('let')
  const ending = count('ending_soon')
  return { total, let: let_, ending, vacant: total - let_ - ending }
})
const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? t('Good morning') : h < 18 ? t('Good afternoon') : t('Good evening')
})
// one plain sentence about today, so the page starts with what matters
const summary = computed(() =>
  data.value.stats.unpaidCount
    ? t('{0} to collect: {1}.', tn(data.value.stats.unpaidCount, '{0} invoice', '{0} invoices'), money(data.value.stats.unpaidTotal))
    : t('Everything is collected. Your properties are up to date.'),
)
</script>
