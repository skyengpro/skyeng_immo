<template>
  <!-- What the unit is like: building, type, rooms, area, furnished -->
  <Panel :title="title || t('The property')" padded>
    <Facts :items="items" />
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
    ...(f.bathrooms ? [{ label: t('Bathrooms'), value: num(f.bathrooms) }] : []),
    ...(f.area ? [{ label: t('Area'), value: `${num(f.area)} m²` }] : []),
    { label: t('Furnished'), value: f.furnished ? t('Yes') : t('No') },
  ]
})
</script>
