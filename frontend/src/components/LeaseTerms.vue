<template>
  <Panel :title="title || t('The lease')" padded>
    <template #actions><StatusBadge kind="lease" :status="lease.status" /></template>
    <Facts :items="items">
      <template #deposit>
        <span class="inline-flex flex-wrap items-center justify-end gap-2">
          <span class="tabular">{{ money(lease.deposit.amount) }}</span>
          <StatusBadge kind="deposit" :status="lease.deposit.status" />
        </span>
      </template>
    </Facts>
    <slot />
  </Panel>
</template>

<script setup>
import { computed } from 'vue'
import Panel from './Panel.vue'
import Facts from './Facts.vue'
import StatusBadge from './StatusBadge.vue'
import { date, money } from '@/format'
import { t } from '@/i18n'

const props = defineProps({ lease: Object, title: String })
const FREQ = { monthly: 'Every month', bimonthly: 'Every 2 months', quarterly: 'Every 3 months', semiannual: 'Every 6 months', annual: 'Once a year' }
const items = computed(() => {
  const l = props.lease
  const rows = [
    { label: t('Start'), value: date(l.startDate) },
    { label: t('End'), value: l.endDate ? date(l.endDate) : t('Open-ended') },
    { label: t('Payment'), value: t(FREQ[l.frequency] || FREQ.monthly) },
    { label: t('Amount each time'), value: money(l.amountPerPeriod) },
  ]
  if (l.lines?.length > 1) for (const line of l.lines) rows.push({ label: `· ${line.label}`, value: money(line.amount) })
  if (l.noticeDays) rows.push({ label: t('Notice'), value: t('{0} days', l.noticeDays) })
  if (l.deposit) rows.push({ label: t('Deposit'), slot: 'deposit' })
  return rows
})
</script>
