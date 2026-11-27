<template>
  <Transition name="drop">
    <div v-if="!net.online || net.stale" class="no-print mx-4 mt-1 flex items-center gap-3 rounded-app border border-warn/20 bg-warn-soft px-4 py-2.5 text-[13px] text-warn md:mx-8 lg:mx-10">
      <span class="lucide-cloud-off size-4 shrink-0" />
      <p class="min-w-0 flex-1">
        <b>{{ t('You are offline.') }}</b>
        {{ net.freshAt ? t('You see the information from {0}.', time(new Date(net.freshAt))) : t('You see the last information saved on this device.') }}
      </p>
    </div>
  </Transition>
</template>

<script setup>
import { net } from '@/api'
import { t } from '@/i18n'
import { time } from '@/format'
</script>

<style scoped>
.drop-enter-active,
.drop-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.drop-enter-from,
.drop-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
