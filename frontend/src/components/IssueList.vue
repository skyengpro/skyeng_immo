<template>
  <ul class="stagger surface divide-y divide-line overflow-hidden">
    <Row v-for="i in issues" :key="i.id" :to="`${base}/maintenance/${encodeURIComponent(i.id)}`">
      <template #lead>
        <span class="flex size-10 shrink-0 items-center justify-center rounded-full" :class="i.urgent ? 'bg-alert-soft text-alert' : 'bg-sky-soft text-sky-mid'">
          <span :class="categoryIcon[i.category] || 'lucide-wrench'" class="size-[18px]" />
        </span>
      </template>
      <p class="truncate text-[14.5px] font-semibold text-ink">{{ i.title }}</p>
      <p v-if="showTenant" class="truncate text-[12.5px] text-ink-soft">{{ [i.tenantName, i.property?.displayName].filter(Boolean).join(' · ') }}</p>
      <p class="text-[12.5px] text-ink-mute">{{ date(i.createdAt) }} · {{ t(categoryLabel[i.category] || 'Something else') }}</p>
      <template #end>
        <StatusBadge kind="approval" :status="i.approval" />
        <span v-if="i.urgent" class="rounded-full bg-alert-soft px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-alert">{{ t('Urgent') }}</span>
      </template>
    </Row>
  </ul>
</template>

<script setup>
import Row from './Row.vue'
import StatusBadge from './StatusBadge.vue'
import { categoryIcon, categoryLabel } from '@/issues'
import { date } from '@/format'
import { t } from '@/i18n'

defineProps({ issues: Array, base: { type: String, required: true }, showTenant: Boolean })
</script>
