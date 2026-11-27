<template>
  <div class="surface">
    <EmptyState icon="lucide-cloud-off" :title="offline ? t('No connection') : t('This page could not be loaded')" :text="error?.message">
      <Btn icon="lucide-rotate-cw" :label="t('Try again')" @click="$emit('retry')" />
    </EmptyState>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EmptyState from './EmptyState.vue'
import Btn from './Btn.vue'
import { OfflineError } from '@/api'
import { t } from '@/i18n'

const props = defineProps({ error: Object })
defineEmits(['retry'])
const offline = computed(() => props.error instanceof OfflineError)
</script>
