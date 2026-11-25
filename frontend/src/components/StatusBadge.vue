<template>
  <span class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-[12px] font-medium" :class="meta.cls">
    <span class="size-1.5 rounded-full" :class="meta.dot" />{{ t(meta.label) }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { t } from '@/i18n'

// kind: invoice, schedule, lease, property, deposit, approval
const props = defineProps({ kind: String, status: String })
const ok = { cls: 'bg-ok-soft text-ok', dot: 'bg-ok' }
const amber = { cls: 'bg-warn-soft text-warn', dot: 'bg-warn-mid' }
const red = { cls: 'bg-alert-soft text-alert', dot: 'bg-alert' }
const blue = { cls: 'bg-info-soft text-info', dot: 'bg-info' }
const gray = { cls: 'bg-paper-deep text-ink-soft', dot: 'bg-ink-faint' }
const STATUS = {
  invoice: { paid: [ok, 'Paid'], due: [amber, 'To pay'], overdue: [red, 'Late'], partly_paid: [amber, 'Partly paid'] },
  schedule: { paid: [ok, 'Paid'], due: [amber, 'To pay'], overdue: [red, 'Late'], partly_paid: [amber, 'Partly paid'], upcoming: [blue, 'Coming'] },
  lease: { active: [ok, 'Current'], upcoming: [blue, 'Starts soon'], notice_given: [amber, 'Notice given'], expired: [gray, 'Ended'] },
  property: { let: [ok, 'Let'], available: [gray, 'Vacant'], ending_soon: [amber, 'Lease ending'], renovation: [amber, 'Being renovated'] },
  deposit: { received: [ok, 'Received'], partly_received: [amber, 'Partly received'], returned: [gray, 'Returned'], requested: [amber, 'Requested'], unknown: [gray, 'Not recorded'] },
  approval: { awaiting_approval: [amber, 'Awaiting approval'], in_progress: [blue, 'In progress'], rejected: [red, 'Rejected'], completed: [ok, 'Completed'] },
}
const meta = computed(() => {
  const [tone, label] = STATUS[props.kind]?.[props.status] || [gray, props.status || '—']
  return { ...tone, label }
})
</script>
