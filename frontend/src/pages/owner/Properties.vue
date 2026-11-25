<template>
  <div>
    <PageHeader :eyebrow="t('Your portfolio')" :title="t('My properties')" :subtitle="t('Every building and unit, who lives there and the rent.')" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="4" />
    <EmptyState v-else-if="!units.length" class="surface" icon="lucide-building-2" :title="t('No property yet')" :text="t('Your property manager adds your properties here.')" />
    <template v-else>
      <Chips v-if="units.length > 3" v-model="filter" class="mb-5" :label="t('Filter')" :options="options" />
      <EmptyState v-if="!shown" class="surface" icon="lucide-search-x" :title="t('No property matches')">
        <Btn :label="t('Show all')" @click="filter = 'all'" />
      </EmptyState>
      <div v-for="section in sections" :key="section.landlord?.id || 'all'" class="mb-8 last:mb-0" :class="data.byLandlord && 'rounded-[22px] bg-paper-deep/60 p-3 md:p-4'">
        <h2 v-if="data.byLandlord" class="mb-3 px-1 font-display text-[22px] text-ink">{{ section.landlord ? t('Landlord: {0}', section.landlord.name) : t('No landlord recorded') }}</h2>
        <section v-for="group in section.groups" :key="group.building?.id || 'solo'" class="mb-6 last:mb-0">
          <div class="mb-3 flex items-center gap-3 px-1">
            <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-sky-soft"><span class="lucide-building-2 size-[18px] text-sky-mid" /></span>
            <div class="min-w-0">
              <h3 class="truncate font-display text-[20px] leading-tight text-ink">{{ group.building?.name || t('Other properties') }}</h3>
              <p class="text-[12.5px] text-ink-mute">{{ tn(group.units.length, '{0} unit', '{0} units') }}</p>
            </div>
          </div>
          <ul class="stagger surface divide-y divide-line overflow-hidden">
            <li class="hidden grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)_150px_130px_16px] gap-x-3 bg-paper/60 px-5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-mute md:grid" aria-hidden="true">
              <span>{{ t('Unit') }}</span><span>{{ t('Tenant') }}</span><span class="text-right">{{ t('Rent') }}</span><span class="text-right">{{ t('Status') }}</span><span />
            </li>
            <li v-for="u in group.units" :key="u.id">
              <RouterLink :to="`/proprietaire/biens/${encodeURIComponent(u.id)}`"
                class="group grid grid-cols-[minmax(0,1fr)_auto_16px] items-center gap-x-3 gap-y-0.5 px-4 py-3.5 transition hover:bg-paper md:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)_150px_130px_16px] md:px-5">
                <div class="min-w-0">
                  <p class="truncate text-[15px] font-semibold text-ink">{{ u.name }}</p>
                  <p class="truncate text-[12.5px] text-ink-mute md:hidden">{{ u.tenantName || t('Vacant, no tenant') }}</p>
                  <p v-if="u.type" class="hidden truncate text-[12.5px] text-ink-mute md:block">{{ u.type }}</p>
                </div>
                <div class="hidden min-w-0 items-center gap-2.5 md:flex">
                  <Initials v-if="u.tenantName" :name="u.tenantName" size="sm" />
                  <span class="truncate text-[13.5px]" :class="u.tenantName ? 'text-ink-soft' : 'text-ink-mute'">{{ u.tenantName || t('Vacant, no tenant') }}</span>
                </div>
                <div class="flex flex-col items-end gap-1.5 md:contents">
                  <span v-if="u.rent.amount > 0" class="whitespace-nowrap text-right text-[14px] font-semibold text-ink tabular">{{ perPeriod(u.rent.amount, u.rent.frequency) }}</span>
                  <span v-else class="hidden text-right text-ink-faint md:block">—</span>
                  <span class="md:justify-self-end"><StatusBadge kind="property" :status="u.status" /></span>
                </div>
                <span class="lucide-chevron-right size-4 text-ink-faint transition group-hover:translate-x-0.5 group-hover:text-ink-soft" />
              </RouterLink>
            </li>
          </ul>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Initials from '@/components/Initials.vue'
import Btn from '@/components/Btn.vue'
import Chips from '@/components/Chips.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { perPeriod } from '@/format'

const { data, error, reload } = useLoad('list_properties')
const filter = ref('all')
const STATUS = [['let', 'Let'], ['available', 'Vacant'], ['ending_soon', 'Lease ending'], ['renovation', 'Being renovated']]
const units = computed(() => (data.value?.sections || []).flatMap((s) => s.groups.flatMap((g) => g.units)))
const count = (v) => (v === 'all' ? units.value.length : units.value.filter((u) => u.status === v).length)
const options = computed(() => [['all', 'All'], ...STATUS].filter(([v]) => v === 'all' || count(v)).map(([value, label]) => ({ value, label: t(label), count: count(value) })))
const shown = computed(() => count(filter.value))
// keep only the units that pass the filter, drop empty buildings and landlords
const sections = computed(() =>
  (data.value?.sections || [])
    .map((s) => ({ ...s, groups: s.groups.map((g) => ({ ...g, units: g.units.filter((u) => filter.value === 'all' || u.status === filter.value) })).filter((g) => g.units.length) }))
    .filter((s) => s.groups.length),
)
</script>
