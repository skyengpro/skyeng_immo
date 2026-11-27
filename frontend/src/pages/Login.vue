<template>
  <!-- phone: everything fits the screen, no scrolling -->
  <div class="flex min-h-[100dvh] flex-col bg-paper lg:grid lg:min-h-screen lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
    <!-- brand panel -->
    <section class="relative shrink-0 overflow-hidden bg-[#0F3357] text-white lg:min-h-screen">
      <div class="absolute inset-0 bg-[radial-gradient(120%_80%_at_0%_0%,#1d5d96_0%,transparent_60%),radial-gradient(90%_70%_at_100%_100%,#0a2540_0%,transparent_70%)]" />
      <Skyline class="pointer-events-none absolute inset-x-0 bottom-0 hidden h-[34%] w-full text-white/[.07] lg:block" />
      <div class="relative flex h-full flex-col justify-between gap-3 px-6 py-4 sm:gap-10 sm:px-10 sm:py-7 lg:px-14 lg:py-12">
        <Logo inverted mark-class="size-9 rounded-app ring-1 ring-white/20 sm:size-11 sm:rounded-app" />
        <div class="max-w-[420px]">
          <p class="eyebrow mb-4 hidden !text-[#a9d4f7] sm:block">{{ t('Landlords and tenants') }}</p>
          <h1 class="max-w-[360px] font-display text-[24px] leading-[1.1] sm:max-w-none sm:text-[44px] lg:max-w-[380px] lg:text-[52px]">
            {{ t('Your properties,') }} <em class="italic text-[#a9d4f7]">{{ t('clear as the sky.') }}</em>
          </h1>
          <ul class="mt-9 hidden space-y-4 text-[15px] text-white/80 sm:block">
            <li v-for="f in features" :key="f.icon" class="flex items-center gap-3.5">
              <span class="flex size-9 items-center justify-center rounded-full border border-white/15 bg-white/[.06]"><span :class="f.icon" class="size-4" /></span>
              {{ t(f.text) }}
            </li>
          </ul>
        </div>
        <p class="hidden text-[12.5px] text-white/50 lg:block">© {{ new Date().getFullYear() }} Sky-immo · {{ t('Rental management made simple') }}</p>
      </div>
    </section>

    <!-- form -->
    <section class="relative flex min-h-0 flex-1 flex-col lg:min-h-screen">
      <div class="flex justify-end p-5 max-lg:absolute max-lg:right-0 max-lg:top-0 max-lg:p-3 sm:p-7">
        <div class="flex items-center rounded-full border border-line bg-card p-0.5" role="group" :aria-label="t('Language')">
          <button v-for="l in ['fr', 'en']" :key="l" class="rounded-full px-3 py-1 text-[11.5px] font-semibold uppercase tracking-wide transition"
            :class="lang === l ? 'bg-ink text-on-ink' : 'text-ink-mute hover:text-ink'" :aria-pressed="lang === l" @click="setLanguage(l)">{{ l }}</button>
        </div>
      </div>
      <div class="flex flex-1 items-center justify-center px-6 py-8 sm:pb-16 sm:pt-0">
        <form class="rise w-full max-w-[380px]" @submit.prevent="submit">
          <h2 class="font-display text-[34px] leading-none text-ink sm:text-[44px]">{{ t('Sign in') }}</h2>
          <p class="mt-2 text-[14px] text-ink-mute sm:mt-3 sm:text-[15px]">{{ t('Follow your home, your properties and your payments.') }}</p>

          <div class="mt-6 space-y-4 sm:mt-9 sm:space-y-5">
            <label class="block">
              <span class="mb-1.5 block text-[13px] font-semibold text-ink">{{ t('Email') }}</span>
              <input v-model="email" :aria-label="t('Email')" type="email" autocomplete="username" inputmode="email" autocapitalize="none" required :placeholder="t('you@example.com')" class="field" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-[13px] font-semibold text-ink">{{ t('Password') }}</span>
              <span class="relative block">
                <input v-model="password" :aria-label="t('Password')" :type="show ? 'text' : 'password'" autocomplete="current-password" required class="field pr-12" />
                <button type="button" class="absolute right-2 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-full text-ink-mute hover:bg-paper hover:text-ink"
                  :aria-label="show ? t('Hide password') : t('Show password')" @click="show = !show">
                  <span :class="show ? 'lucide-eye-off' : 'lucide-eye'" class="size-4" />
                </button>
              </span>
            </label>
            <p v-if="error" role="alert" class="flex items-center gap-2 rounded-app bg-alert-soft px-3.5 py-2.5 text-[13px] text-alert">
              <span class="lucide-circle-alert size-4 shrink-0" />{{ error }}
            </p>
            <Btn type="submit" variant="primary" size="lg" block :loading="loading" :label="t('Sign in')" class="!mt-6 sm:!mt-7" />
          </div>
          <p class="mt-4 text-center text-[13px] sm:mt-5">
            <RouterLink to="/mot-de-passe-oublie" class="font-medium text-ink-soft underline decoration-line-strong underline-offset-4 hover:text-ink">{{ t('I forgot my password') }}</RouterLink>
          </p>
          <p class="mt-6 flex items-start gap-2 border-t border-line pt-5 text-[12px] leading-relaxed text-ink-mute sm:mt-10">
            <span class="lucide-mail mt-px size-3.5 shrink-0 text-sky-mid" />
            {{ t('No account yet? Your property manager sends you an invitation by email. Follow its link to choose your password.') }}
          </p>
        </form>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Logo from '@/components/Logo.vue'
import Btn from '@/components/Btn.vue'
import Skyline from '@/components/Skyline.vue'
import { lang, setLanguage, t } from '@/i18n'
import { login } from '@/session'

const email = ref('')
const password = ref('')
const show = ref(false)
const error = ref('')
const loading = ref(false)
const features = [
  { icon: 'lucide-building-2', text: 'Every property and unit at a glance' },
  { icon: 'lucide-receipt-text', text: 'Rent, invoices and receipts in one place' },
  { icon: 'lucide-wrench', text: 'Repairs reported and approved in a tap' },
  { icon: 'lucide-wifi-off', text: 'Still opens when the internet is down' },
]

async function submit() {
  error.value = ''
  if (!email.value.trim() || !password.value) {
    error.value = t('Enter your email address and your password.')
    return
  }
  loading.value = true
  try {
    await login(email.value.trim(), password.value)
  } catch (e) {
    error.value = !navigator.onLine || e instanceof TypeError ? t('You are offline. Signing in needs a connection.') : e.status === 401 ? t('Wrong email address or password.') : t('Could not sign in. Please try again.')
    loading.value = false
  }
}
</script>
