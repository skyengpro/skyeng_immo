<template>
  <!-- share of units let, ending and vacant -->
  <Panel :title="t('Occupancy')" padded>
    <div class="flex items-baseline justify-between">
      <span class="font-display text-[34px] leading-none text-ink tabular">{{ rate }}<span class="text-[18px] text-ink-mute">%</span></span>
      <span class="text-[12.5px] text-ink-mute">{{ letLabel }}</span>
    </div>
    <div class="mt-3 flex h-2.5 overflow-hidden rounded-full bg-paper-deep" role="img" :aria-label="letLabel">
      <span class="bg-ok transition-[width] duration-700" :style="{ width: `${(occupancy.let / occupancy.total) * 100}%` }" />
      <span class="bg-warn-mid" :style="{ width: `${(occupancy.ending / occupancy.total) * 100}%` }" />
    </div>
    <ul class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[12.5px] text-ink-mute">
      <li class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-ok" />{{ t('Let') }} · {{ occupancy.let }}</li>
      <li v-if="occupancy.ending" class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-warn-mid" />{{ t('Lease ending') }} · {{ occupancy.ending }}</li>
      <li class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-paper-deep ring-1 ring-line-strong" />{{ t('Vacant') }} · {{ occupancy.vacant }}</li>
    </ul>
  </Panel>
</template>

<script setup>
import { computed } from 'vue'
import Panel from './Panel.vue'
import { t } from '@/i18n'

// { total, let, ending, vacant }, total > 0
const props = defineProps({ occupancy: { type: Object, required: true } })
const rate = computed(() => Math.round(((props.occupancy.let + props.occupancy.ending) / props.occupancy.total) * 100))
const letLabel = computed(() => t(props.occupancy.let === 1 ? '{0} unit let out of {1}' : '{0} units let out of {1}', props.occupancy.let, props.occupancy.total))
</script>
