<template>
  <!-- desktop: centred dialog; phone: bottom sheet with the same content and buttons -->
  <Dialog v-if="!mobile" :open="open" :title="title" :message="message" :size="size" @update:open="emit('update:open', $event)">
    <slot />
    <template v-if="$slots.actions" #actions>
      <div class="flex w-full justify-end gap-2"><slot name="actions" /></div>
    </template>
  </Dialog>
  <BottomSheet v-else :open="open" @update:open="emit('update:open', $event)">
    <div class="px-5 pb-[calc(env(safe-area-inset-bottom)+16px)] pt-1">
      <div class="mb-4">
        <h3 class="font-display text-[22px] leading-tight text-ink">{{ title }}</h3>
        <p v-if="message" class="mt-1 text-[13px] leading-snug text-ink-mute">{{ message }}</p>
      </div>
      <slot />
      <div v-if="$slots.actions" class="mt-5 grid grid-cols-2 gap-2 [&>*:only-child]:col-span-2 [&>*]:h-12 [&>*]:w-full"><slot name="actions" /></div>
    </div>
  </BottomSheet>
</template>

<script setup>
import { BottomSheet, Dialog } from 'frappe-ui'
import { useMediaQuery } from '@vueuse/core'

defineProps({ open: Boolean, title: String, message: String, size: { type: String, default: 'lg' } })
const emit = defineEmits(['update:open'])
const mobile = useMediaQuery('(max-width: 767px)')
</script>
