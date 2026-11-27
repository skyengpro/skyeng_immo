<template>
  <div>
    <EmptyState v-if="!lines.length" icon="lucide-calendar-days" :title="t('No rent schedule yet')" :text="t('The rent periods appear here once the lease is set up.')" />
    <template v-else>
      <ul class="stagger surface divide-y divide-line overflow-hidden">
        <Row v-for="line in visible" :key="line.id" :to="line.invoiceId ? `${base}/factures/${encodeURIComponent(line.invoiceId)}` : undefined">
          <p class="text-balance text-[14.5px] font-semibold text-ink">{{ period(line.periodStart, line.periodEnd) }}</p>
          <p class="text-[12.5px] text-ink-mute">{{ line.status === 'upcoming' ? t('Invoice not issued yet') : t('Due on {0}', date(line.dueDate)) }}</p>
          <template #end>
            <span class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ money(line.amount) }}</span>
            <StatusBadge kind="schedule" :status="line.status" />
          </template>
        </Row>
      </ul>
      <div v-if="hidden > 0" class="mt-3"><Btn block icon="lucide-chevrons-down" :label="t('Show the whole schedule ({0})', lines.length)" @click="all = true" /></div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Row from './Row.vue'
import Btn from './Btn.vue'
import EmptyState from './EmptyState.vue'
import StatusBadge from './StatusBadge.vue'
import { date, money, period } from '@/format'
import { t } from '@/i18n'

const props = defineProps({ lines: { type: Array, default: () => [] }, base: { type: String, required: true } })
const PREVIEW = 6
const all = ref(false)
// start at the first line still to pay (or to come), keep the two before it for context
const start = computed(() => {
  if (all.value) return 0
  const open = props.lines.findIndex((l) => l.status !== 'paid')
  return Math.max(0, (open === -1 ? props.lines.length - PREVIEW : open) - 2)
})
const visible = computed(() => (all.value ? props.lines : props.lines.slice(start.value, start.value + PREVIEW)))
const hidden = computed(() => props.lines.length - visible.value.length)
</script>
