<template>
  <div>
    <PageHeader :eyebrow="t('Your portfolio')" :title="t('Tenants')" :subtitle="t('Every tenant of your properties, current or former.')" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="4" />
    <EmptyState v-else-if="!data.tenants.length" class="surface" icon="lucide-users-round" :title="t('No tenant yet')" :text="t('Tenants appear here once your property manager records a lease.')" />
    <template v-else>
      <Chips v-model="filter" class="mb-5" :label="t('Filter')" :options="options" />
      <EmptyState v-if="!shown.length" class="surface" icon="lucide-search-x" :title="t('No tenant matches')">
        <Btn :label="t('Show all')" @click="filter = 'all'" />
      </EmptyState>
      <section v-for="section in sections" :key="section.landlord?.id || 'all'" class="mb-8 last:mb-0">
        <h2 v-if="data.byLandlord" class="mb-3 px-1 font-display text-[22px] text-ink">{{ section.landlord ? t('Landlord: {0}', section.landlord.name) : t('No landlord recorded') }}</h2>
        <ul class="stagger surface divide-y divide-line overflow-hidden">
          <Row v-for="tenant in section.tenants" :key="tenant.id" :to="`/proprietaire/baux/${encodeURIComponent(tenant.leaseId)}`">
            <template #lead><Initials :name="tenant.name" /></template>
            <p class="truncate text-[15px] font-semibold text-ink">{{ tenant.name }}</p>
            <p class="truncate text-[12.5px] text-ink-mute">{{ tenant.units.map((unit) => unit.displayName).join(', ') }}</p>
            <template #end>
              <StatusBadge kind="lease" :status="tenant.current ? 'active' : 'expired'" />
              <span class="text-[12px] text-ink-mute">{{ period(tenant) }}</span>
            </template>
          </Row>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Row from '@/components/Row.vue'
import Initials from '@/components/Initials.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import Chips from '@/components/Chips.vue'
import Btn from '@/components/Btn.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { date } from '@/format'
import { t } from '@/i18n'

const { data, error, reload } = useLoad('list_tenants')
const filter = ref('all')

const count = (value) => (data.value?.tenants || []).filter((tenant) => value === 'all' || tenant.current === (value === 'current')).length
const options = computed(() =>
  [['all', 'All'], ['current', 'Current tenants'], ['former', 'Former tenants']].map(([value, label]) => ({ value, label: t(label), count: count(value) })),
)
const shown = computed(() => (data.value?.tenants || []).filter((tenant) => filter.value === 'all' || tenant.current === (filter.value === 'current')))

// For staff over several landlords: one section per landlord, in the order the server sorted.
const sections = computed(() => {
  const groups = new Map()
  for (const tenant of shown.value) {
    const key = tenant.landlord?.id || ''
    if (!groups.has(key)) groups.set(key, { landlord: tenant.landlord, tenants: [] })
    groups.get(key).tenants.push(tenant)
  }
  return [...groups.values()]
})

const period = (tenant) =>
  tenant.current ? t('Since {0}', date(tenant.startDate)) : tenant.endDate ? t('Until {0}', date(tenant.endDate)) : date(tenant.startDate)
</script>
