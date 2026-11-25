<template>
  <div v-if="showInstall" class="no-print mx-4 mt-1 flex items-center gap-3 rounded-[14px] border border-line bg-card px-4 py-2.5 shadow-card md:hidden">
    <Logo mark-only mark-class="size-8" />
    <p class="min-w-0 flex-1 text-[13px] text-ink-soft">
      {{ install.ios ? t('Add Sky-immo to your home screen: Share, then Add to Home Screen.') : t('Install Sky-immo on this phone, it opens like an app.') }}
    </p>
    <Btn v-if="!install.ios" size="sm" variant="brand" :label="t('Install')" @click="installApp" />
    <button class="flex size-8 items-center justify-center rounded-full text-ink-mute hover:bg-paper" :aria-label="t('Close')" @click="dismissInstall">
      <span class="lucide-x size-4" />
    </button>
  </div>
</template>

<script setup>
import Logo from './Logo.vue'
import Btn from './Btn.vue'
import { install, showInstall, installApp, dismissInstall } from '@/install'
import { t } from '@/i18n'
</script>
