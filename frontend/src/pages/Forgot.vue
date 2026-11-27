<template>
  <div class="flex min-h-[100dvh] flex-col bg-paper">
    <div class="flex items-center justify-between p-5 sm:p-7">
      <RouterLink to="/connexion"><Logo mark-class="size-9" /></RouterLink>
    </div>
    <div class="flex flex-1 items-center justify-center px-6 pb-16">
      <div class="rise w-full max-w-[380px]">
        <RouterLink to="/connexion" class="mb-4 inline-flex items-center gap-1.5 text-[13px] font-medium text-ink-mute hover:text-ink">
          <span class="lucide-arrow-left size-3.5" /> {{ t('Back to sign in') }}
        </RouterLink>
        <h1 class="font-display text-[34px] leading-none text-ink sm:text-[40px]">{{ t('Forgotten password') }}</h1>
        <template v-if="!sent">
          <p class="mt-3 text-[14px] text-ink-mute sm:text-[15px]">{{ t('Enter your email address. We send you a link to choose a new password.') }}</p>
          <form class="mt-7 space-y-5" @submit.prevent="submit">
            <label class="block">
              <span class="mb-1.5 block text-[13px] font-semibold text-ink">{{ t('Email') }}</span>
              <input v-model="email" type="email" autocomplete="username" inputmode="email" autocapitalize="none" required class="field" />
            </label>
            <p v-if="error" role="alert" class="rounded-app bg-alert-soft px-3.5 py-2.5 text-[13px] text-alert">{{ error }}</p>
            <Btn type="submit" variant="primary" size="lg" block :loading="loading" :label="t('Send the link')" />
          </form>
        </template>
        <div v-else class="surface mt-7 flex items-start gap-3 p-5">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-ok-soft"><span class="lucide-mail-check size-5 text-ok" /></span>
          <p class="text-[14px] text-ink-soft">{{ t('If an account uses this address, an email is on its way. Check your inbox, then follow the link.') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Logo from '@/components/Logo.vue'
import Btn from '@/components/Btn.vue'
import { t } from '@/i18n'

const email = ref('')
const sent = ref(false)
const error = ref('')
const loading = ref(false)

// same answer whether the account exists or not, so addresses cannot be probed
async function submit() {
  error.value = ''
  loading.value = true
  try {
    await fetch('/api/method/frappe.core.doctype.user.user.reset_password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ user: email.value.trim() }),
    })
    sent.value = true
  } catch {
    error.value = t('You are offline. This needs a connection, please try again when you are back online.')
  } finally {
    loading.value = false
  }
}
</script>
