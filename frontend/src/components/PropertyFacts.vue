<template>
  <!-- What the unit is like: the facts of the desk form that matter to someone living there -->
  <Panel :title="title || t('The property')" padded>
    <Facts :items="items" />
    <div v-if="features.amenities?.length" class="mt-4 border-t border-line pt-3.5">
      <p class="mb-2 text-[13.5px] text-ink-mute">{{ t('Amenities') }}</p>
      <ul class="flex flex-wrap gap-1.5">
        <li v-for="a in features.amenities" :key="a" class="rounded-full bg-sky-soft px-2.5 py-1 text-[12.5px] font-medium text-sky-mid">{{ t(a) }}</li>
      </ul>
    </div>
    <div v-if="features.description" class="mt-4 border-t border-line pt-3.5">
      <p class="mb-1 text-[13.5px] text-ink-mute">{{ t('Description') }}</p>
      <p class="whitespace-pre-line text-[14px] leading-relaxed text-ink-soft">{{ features.description }}</p>
    </div>
  </Panel>
</template>

<script setup>
import { computed } from 'vue'
import Panel from './Panel.vue'
import Facts from './Facts.vue'
import { num } from '@/format'
import { t } from '@/i18n'

const props = defineProps({ features: { type: Object, required: true }, buildingName: String, title: String })
const items = computed(() => {
  const f = props.features
  return [
    ...(props.buildingName ? [{ label: t('Building'), value: props.buildingName }] : []),
    ...(f.type ? [{ label: t('Type'), value: f.type }] : []),
    ...(f.bedrooms ? [{ label: t('Bedrooms'), value: num(f.bedrooms) }] : []),
    ...(f.masterBedrooms ? [{ label: t('Master bedrooms'), value: num(f.masterBedrooms) }] : []),
    ...(f.bathrooms ? [{ label: t('Bathrooms'), value: num(f.bathrooms) }] : []),
    ...(f.area ? [{ label: t('Area'), value: `${num(f.area)} m²` }] : []),
    ...(f.parking ? [{ label: t('Parking spaces'), value: num(f.parking) }] : []),
    { label: t('Furnished'), value: f.furnished ? t('Yes') : t('No') },
    ...(f.smoking !== undefined ? [{ label: t('Smoking allowed'), value: f.smoking ? t('Yes') : t('No') }] : []),
  ]
})
</script>
