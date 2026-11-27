<template>
  <div class="space-y-3" role="status" :aria-label="t('Loading')">
    <div v-if="stats" class="grid grid-cols-2 gap-3 md:gap-4 lg:grid-cols-4">
      <div v-for="i in 4" :key="i" class="surface h-[104px] animate-pulse md:h-[124px]" />
    </div>
    <div v-for="i in rows" :key="'r' + i" class="surface animate-pulse" :class="tall ? 'h-40' : 'h-[72px]'" />
  </div>
</template>

<script setup>
import { t } from '@/i18n'
defineProps({ rows: { type: Number, default: 4 }, stats: Boolean, tall: Boolean })
</script>
