<template>
  <!-- one line of a list: the whole row opens the detail -->
  <li>
    <component :is="to ? 'RouterLink' : 'div'" :to="to" class="group flex items-center gap-3 px-4 py-3.5 transition md:px-5" :class="to && 'hover:bg-paper'">
      <slot name="lead" />
      <div class="min-w-0 flex-1"><slot /></div>
      <div v-if="$slots.end" class="flex shrink-0 flex-col items-end gap-1.5 text-right"><slot name="end" /></div>
      <span v-if="to" class="lucide-chevron-right size-4 shrink-0 text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-ink-soft" />
    </component>
  </li>
</template>

<script setup>
defineProps({ to: [String, Object] })
</script>
