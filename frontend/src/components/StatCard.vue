<template>
  <component :is="to ? 'RouterLink' : 'div'" :to="to"
    class="surface rise group relative flex min-h-[104px] flex-col justify-between overflow-hidden p-4 transition duration-200 md:min-h-[124px] md:p-5"
    :class="to && 'hover:-translate-y-0.5 hover:shadow-lift'">
    <!-- the icon as a large faded mark in the background -->
    <span :class="[icon, marks[tone]]" aria-hidden="true"
      class="pointer-events-none absolute -bottom-3 -right-4 size-[68px] opacity-[0.09] transition duration-300 group-hover:-rotate-6 group-hover:scale-110 group-hover:opacity-[0.17] md:-bottom-4 md:-right-4 md:size-[100px]" />

    <p class="relative text-[12.5px] font-medium leading-snug text-ink-soft md:text-[13.5px]">{{ label }}</p>
    <div class="relative mt-2 min-w-0">
      <div class="flex flex-wrap items-baseline gap-x-1.5">
        <span class="font-display leading-none tabular" :class="[valueTones[tone], small ? 'whitespace-nowrap text-[22px] md:text-[26px] xl:text-[32px]' : 'text-[34px] md:text-[44px]']">{{ value }}</span>
        <span v-if="unit" class="text-[12.5px] text-ink-mute">{{ unit }}</span>
      </div>
      <p v-if="hint" class="mt-1.5 flex items-center gap-1.5 text-[11.5px] leading-snug md:text-[12.5px]" :class="hintTone ? hintTones[hintTone] : 'text-ink-mute'">
        <span v-if="hintTone" class="size-1.5 shrink-0 rounded-full bg-current" />{{ hint }}
      </p>
    </div>
  </component>
</template>

<script setup>
defineProps({ label: String, value: [String, Number], unit: String, icon: { type: String, default: 'lucide-circle' },
  hint: String, hintTone: String, to: [String, Object], tone: { type: String, default: 'sky' }, small: Boolean })
const marks = { sky: 'text-sky-mid', ok: 'text-ok', amber: 'text-warn', red: 'text-alert', ink: 'text-ink' }
const valueTones = { sky: 'text-ink', ok: 'text-ink', ink: 'text-ink', amber: 'text-warn', red: 'text-alert' }
const hintTones = { red: 'text-alert', amber: 'text-warn', ok: 'text-ok' }
</script>
