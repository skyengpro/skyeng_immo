<template>
  <!-- segmented tabs: one part of a page at a time (unlike Chips, which filter one list) -->
  <div class="flex w-full gap-1 rounded-app border border-line bg-paper-deep/70 p-1 sm:inline-flex sm:w-auto" role="tablist" :aria-label="label">
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
defineProps({ modelValue: String, options: Array, label: String })
defineEmits(['update:modelValue'])
</script>
