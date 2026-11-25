<template>
  <ul class="stagger surface divide-y divide-line overflow-hidden">
    <Row v-for="inv in invoices" :key="inv.id" :to="`${base}/factures/${encodeURIComponent(inv.id)}`">
      <p class="text-balance text-[14.5px] font-semibold text-ink">{{ showTenant ? inv.tenant.name : period(inv.periodStart, inv.periodEnd) }}</p>
      <p v-if="showTenant" class="truncate text-[12.5px] text-ink-soft">{{ period(inv.periodStart, inv.periodEnd) }}</p>
      <p class="text-[12.5px] text-ink-mute">{{ inv.outstanding > 0 ? t('Due on {0}', date(inv.dueDate)) : t('No. {0}', inv.id) }}</p>
      <template #end>
        <span class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ money(inv.outstanding > 0 ? inv.outstanding : inv.total) }}</span>
        <StatusBadge kind="invoice" :status="inv.status" />
      </template>
    </Row>
  </ul>
</template>

<script setup>
import Row from './Row.vue'
import StatusBadge from './StatusBadge.vue'
import { date, money, period } from '@/format'
import { t } from '@/i18n'

defineProps({ invoices: Array, base: { type: String, required: true }, showTenant: Boolean })
</script>
