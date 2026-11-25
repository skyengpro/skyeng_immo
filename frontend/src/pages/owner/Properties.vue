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
            <Row v-for="u in group.units" :key="u.id" :to="`/proprietaire/biens/${encodeURIComponent(u.id)}`">
              <p class="truncate text-[15px] font-semibold text-ink">{{ u.name }}</p>
              <p class="truncate text-[13px]" :class="u.tenantName ? 'text-ink-soft' : 'text-ink-mute'">{{ u.tenantName || t('Vacant, no tenant') }}</p>
              <p v-if="u.type" class="text-[12px] text-ink-mute">{{ u.type }}</p>
              <template #end>
                <span v-if="u.rent.amount > 0" class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ perPeriod(u.rent.amount, u.rent.frequency) }}</span>
                <StatusBadge kind="property" :status="u.status" />
              </template>
            </Row>
          </ul>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Row from '@/components/Row.vue'
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
