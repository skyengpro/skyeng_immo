<template>
  <div class="scrollbar-none -mx-4 flex gap-1.5 overflow-x-auto px-4 md:mx-0 md:flex-wrap md:px-0" role="group" :aria-label="label">
    <button v-for="o in options" :key="o.value" type="button" :aria-pressed="modelValue === o.value"
      class="flex shrink-0 items-center gap-2 rounded-full border px-3.5 py-1.5 text-[13px] font-medium transition"
      :class="modelValue === o.value ? 'border-ink bg-ink text-on-ink' : 'border-line bg-card text-ink-soft hover:border-line-strong hover:text-ink'"
      @click="$emit('update:modelValue', o.value)">
      {{ o.label }}
      <span v-if="o.count !== undefined" class="tabular" :class="modelValue === o.value ? 'text-on-ink/60' : 'text-ink-faint'">{{ o.count }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({ modelValue: String, options: Array, label: String })
defineEmits(['update:modelValue'])
</script>
