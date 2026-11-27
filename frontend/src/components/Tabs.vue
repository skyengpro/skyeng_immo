<template>
  <!-- segmented tabs: one part of a page at a time (unlike Chips, which filter one list).
       `cards`: side-by-side buttons with the icon above the label, like the section jumps on a phone -->
  <div v-if="cards" class="grid gap-2" role="tablist" :aria-label="label" :style="{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }">
    <button v-for="o in options" :key="o.value" type="button" role="tab" :aria-selected="modelValue === o.value"
      class="relative flex min-w-0 flex-col items-center justify-center gap-1 rounded-app border px-1.5 py-2.5 text-[12px] font-semibold leading-tight transition"
      :class="modelValue === o.value ? 'border-ink bg-ink text-on-ink' : 'border-line bg-card text-ink-soft shadow-card'"
      @click="$emit('update:modelValue', o.value)">
      <span v-if="o.icon" :class="o.icon" class="size-4 shrink-0" />
      <span class="text-center">{{ o.label }}</span>
      <span v-if="o.count" class="tabular absolute right-2 top-1.5 rounded-full px-1.5 text-[11px]"
        :class="modelValue === o.value ? 'text-on-ink/70' : o.tone === 'red' ? 'bg-alert-soft text-alert' : 'text-ink-faint'">{{ o.count }}</span>
    </button>
  </div>
  <div v-else class="flex w-full gap-1 rounded-app border border-line bg-paper-deep/70 p-1 sm:inline-flex sm:w-auto" role="tablist" :aria-label="label">
    <button v-for="o in options" :key="o.value" type="button" role="tab" :aria-selected="modelValue === o.value"
      class="flex min-w-0 flex-1 items-center justify-center gap-2 rounded-app px-4 py-2 text-[13.5px] font-semibold transition sm:flex-none"
      :class="modelValue === o.value ? 'bg-card text-ink shadow-card' : 'text-ink-mute hover:text-ink'"
      @click="$emit('update:modelValue', o.value)">
      <span class="truncate">{{ o.label }}</span>
      <span v-if="o.count !== undefined" class="tabular text-[12px]" :class="modelValue === o.value ? 'text-ink-mute' : 'text-ink-faint'">{{ o.count }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({ modelValue: String, options: Array, label: String, cards: Boolean })
defineEmits(['update:modelValue'])
</script>
