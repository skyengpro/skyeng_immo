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
        <StatCard :label="t('Tenants')" :value="num(data.stats.tenants)" icon="lucide-users-round" />
        <StatCard :label="t('Received this month')" :value="money(data.stats.collectedThisMonth)" icon="lucide-wallet" tone="ok" small />
        <StatCard :label="t('Still to collect')" :value="money(data.stats.unpaidTotal)" icon="lucide-circle-alert" small
          :tone="data.stats.unpaidTotal ? 'red' : 'ok'" :hint-tone="data.stats.unpaidTotal ? 'red' : null"
          :hint="tn(data.stats.unpaidCount, '{0} invoice', '{0} invoices')" />
      </div>

      <p class="eyebrow mb-3 mt-8">{{ t('Late invoices') }}</p>
      <Panel>
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
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Btn from '@/components/Btn.vue'
import StatCard from '@/components/StatCard.vue'
import Panel from '@/components/Panel.vue'
import Row from '@/components/Row.vue'
import Initials from '@/components/Initials.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { longDate, money, num } from '@/format'
import { session } from '@/session'

const { data, error, reload } = useLoad('get_owner_dashboard')
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
