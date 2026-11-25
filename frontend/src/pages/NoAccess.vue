<template>
  <div class="flex min-h-[100dvh] items-center justify-center bg-paper px-6">
    <div class="surface max-w-md">
      <EmptyState icon="lucide-shield-alert" :title="t('This account has no access to Sky-immo')" :text="t('Ask your property manager to give you access, then sign in again.')">
        <Btn variant="primary" icon="lucide-log-out" :label="t('Sign out')" @click="logout" />
      </EmptyState>
    </div>
  </div>
</template>

<script setup>
import EmptyState from '@/components/EmptyState.vue'
import Btn from '@/components/Btn.vue'
import { logout } from '@/session'
import { t } from '@/i18n'
</script>
