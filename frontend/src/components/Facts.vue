<template>
  <!-- label on the left, value on the right; long values wrap under their label on a narrow screen -->
  <dl class="divide-y divide-line">
    <div v-for="(item, i) in items" :key="i" class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5 py-2.5 first:pt-0 last:pb-0">
      <dt class="text-[13.5px] text-ink-mute">{{ item.label }}</dt>
      <dd class="min-w-0 text-right text-[14px] font-semibold text-ink [overflow-wrap:anywhere]">
        <slot :name="item.slot" v-bind="item">{{ item.value }}</slot>
      </dd>
    </div>
  </dl>
</template>

<script setup>
defineProps({ items: Array })
</script>
