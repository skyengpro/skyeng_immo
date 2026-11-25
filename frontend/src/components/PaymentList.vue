<template>
  <EmptyState v-if="!payments.length" class="surface" icon="lucide-banknote" :title="t('No payment yet')" :text="t('Payments appear here as soon as they are recorded.')" />
  <ul v-else class="stagger surface divide-y divide-line overflow-hidden">
    <li v-for="p in payments" :key="`${p.id}-${p.invoiceId}`" class="flex items-center gap-3 px-4 py-3.5 md:px-5">
      <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-ok-soft"><span class="lucide-banknote size-[18px] text-ok" /></span>
      <div class="min-w-0 flex-1">
        <p class="text-[14.5px] font-semibold text-ink">{{ t('Paid on {0}', date(p.date)) }}</p>
        <p class="truncate text-[12.5px] text-ink-mute">{{ [p.mode, p.reference, showInvoice && p.invoiceId].filter(Boolean).join(' · ') }}</p>
      </div>
      <div class="flex shrink-0 flex-col items-end gap-1">
        <span class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ money(p.amount) }}</span>
        <a :href="downloadUrl('receipt', p.id)" target="_blank" rel="noopener" class="inline-flex items-center gap-1 text-[12.5px] font-medium text-sky-mid hover:underline">
          <span class="lucide-download size-3.5" />{{ t('Receipt') }}
        </a>
      </div>
    </li>
  </ul>
</template>

<script setup>
import EmptyState from './EmptyState.vue'
import { downloadUrl } from '@/api'
import { date, money } from '@/format'
import { t } from '@/i18n'

defineProps({ payments: { type: Array, default: () => [] }, showInvoice: Boolean })
</script>
