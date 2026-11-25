<template>
  <div class="flex items-center gap-3">
    <svg viewBox="0 0 512 512" :class="markClass" class="shrink-0" aria-hidden="true">
      <defs>
        <linearGradient :id="`${uid}-bg`" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1C5A92" /><stop offset="1" stop-color="#0D2E4E" /></linearGradient>
        <linearGradient :id="`${uid}-sun`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C6E6FF" /><stop offset="1" stop-color="#62B3F0" /></linearGradient>
        <linearGradient :id="`${uid}-wall`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" /><stop offset="1" stop-color="#DDE9F4" /></linearGradient>
      </defs>
      <rect width="512" height="512" rx="120" :fill="`url(#${uid}-bg)`" />
      <circle class="logo-sun" cx="352" cy="164" r="58" :fill="`url(#${uid}-sun)`" />
      <path class="logo-roof" pathLength="1" d="M112 262 L256 128 L400 262" fill="none" stroke="#fff" stroke-width="38" stroke-linecap="round" stroke-linejoin="round" />
      <rect x="152" y="268" width="208" height="148" rx="26" :fill="`url(#${uid}-wall)`" />
      <rect x="184" y="298" width="40" height="34" rx="10" fill="#1C5A92" />
      <rect x="288" y="298" width="40" height="34" rx="10" fill="#1C5A92" />
      <rect x="232" y="352" width="48" height="64" rx="14" fill="#123B63" />
    </svg>
    <div v-if="!markOnly" class="min-w-0 leading-none">
      <div class="font-display text-[22px] leading-none" :class="inverted ? 'text-white' : 'text-ink'">
        Sky<em class="italic" :class="inverted ? 'text-[#a9d4f7]' : 'text-sky-mid'">-immo</em>
      </div>
      <div v-if="subtitle" class="eyebrow mt-1.5 truncate !text-[10px]" :class="inverted && '!text-white/60'">{{ subtitle }}</div>
    </div>
  </div>
</template>

<script setup>
import { useId } from 'vue'

// each logo has its own gradient ids: a hidden copy (the sidebar on a phone) must not hold the ones another copy uses
const uid = `si${useId()}`
defineProps({ markOnly: Boolean, subtitle: String, inverted: Boolean, markClass: { type: String, default: 'size-10' } })
</script>
