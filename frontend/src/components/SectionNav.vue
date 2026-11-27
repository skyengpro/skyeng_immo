<template>
  <!-- Phone only: buttons that jump to each section of a long page, so nothing hides below the fold.
       Sticks under the top bar and lights up the section being read. Up to three buttons share the
       width; more scroll sideways. -->
  <nav ref="bar" class="no-print sticky top-[60px] z-10 -mx-4 mb-4 bg-paper/90 px-4 py-2 backdrop-blur-md md:hidden" :aria-label="label">
    <div :class="items.length <= 3 ? 'grid gap-2' : 'scrollbar-none flex gap-2 overflow-x-auto'" :style="items.length <= 3 ? { gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` } : undefined">
      <!-- side by side: icon above the label, so the whole label fits; scrolling: icon beside it -->
      <button v-for="item in items" :key="item.id" type="button"
        class="relative flex min-w-0 items-center justify-center rounded-app border font-semibold transition"
        :class="[active === item.id ? 'border-ink bg-ink text-on-ink' : 'border-line bg-card text-ink-soft shadow-card',
          items.length > 3 ? 'shrink-0 gap-1.5 px-3 py-2 text-[12.5px]' : 'flex-col gap-1 px-1.5 py-2 text-[12px] leading-tight']"
        :aria-current="active === item.id ? 'location' : undefined" @click="go(item.id)">
        <span v-if="item.icon" :class="item.icon" class="size-4 shrink-0" />
        <span class="text-center" :class="items.length > 3 && 'truncate'">{{ item.label }}</span>
        <span v-if="item.count" class="tabular text-[11px]"
          :class="[active === item.id ? 'text-on-ink/70' : 'text-ink-faint', items.length <= 3 && 'absolute right-2 top-1.5']">{{ item.count }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({ items: Array, label: String })
const bar = ref(null)
const active = ref(null)
let observer = null
let lock = 0

// Height hidden by the sticky top bar and this bar: a section scrolled to lands just below them.
// Computed here rather than with CSS scroll-margin, which Chrome ignores on these sections.
const covered = () => (document.querySelector('header')?.offsetHeight || 60) + (bar.value?.offsetHeight || 0) + 12

function go(id) {
  const el = document.getElementById(id)
  if (!el) return
  active.value = id
  // the smooth scroll passes over other sections: keep the tapped one lit until it settles
  lock = Date.now() + 900
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - covered(), behavior: 'smooth' })
}

function observe() {
  observer?.disconnect()
  if (!('IntersectionObserver' in window)) return
  // a section is "being read" when it crosses the band just under the sticky bars
  observer = new IntersectionObserver(
    (entries) => {
      if (Date.now() < lock) return
      const seen = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      if (seen.length) active.value = seen[0].target.id
    },
    { rootMargin: `-${covered()}px 0px -55% 0px` },
  )
  for (const item of props.items) {
    const el = document.getElementById(item.id)
    if (el) observer.observe(el)
  }
}

onMounted(observe)
watch(() => props.items.map((i) => i.id).join(), () => setTimeout(observe))
onBeforeUnmount(() => observer?.disconnect())
</script>
