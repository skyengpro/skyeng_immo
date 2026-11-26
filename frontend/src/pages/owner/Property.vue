<template>
  <div>
    <PageHeader :eyebrow="data?.buildingName" :title="data?.name || t('Property')" :back="'/proprietaire/biens'" :back-label="t('My properties')">
      <template v-if="data" #meta><div class="mt-3"><StatusBadge kind="property" :status="data.status" /></div></template>
    </PageHeader>

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" tall />
    <div v-else class="grid grid-cols-[minmax(0,1fr)] gap-4 md:grid-cols-[minmax(0,1fr)_320px] md:items-start md:gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-6">
      <aside class="space-y-4 md:order-2 md:sticky md:top-20">
        <Panel :title="t('The property')" padded>
          <Facts :items="features" />
        </Panel>
        <LeaseTerms v-if="data.currentLease" :lease="data.currentLease" :title="t('Current lease')">
          <div class="mt-4 rounded-[14px] bg-paper-deep/70 p-4">
            <p class="eyebrow mb-2">{{ t('Tenant') }}</p>
            <div class="flex items-center gap-3">
              <Initials :name="data.currentLease.tenant.name" />
              <div class="min-w-0">
                <p class="truncate text-[15px] font-semibold text-ink">{{ data.currentLease.tenant.name }}</p>
                <p class="text-[12.5px] text-ink-mute">{{ t('Moved in on {0}', date(data.currentLease.startDate)) }}</p>
              </div>
            </div>
          </div>
          <Btn class="mt-4" variant="primary" block icon="lucide-user-round" :label="t('See the tenant and their payments')" :to="leaseHref(data.currentLease.id)" />
        </LeaseTerms>
        <Panel v-else :title="t('Current lease')" padded>
          <p class="text-[14px] text-ink-mute">{{ t('This property is vacant. No lease is running.') }}</p>
        </Panel>
      </aside>

      <div class="min-w-0 space-y-8 md:order-1">
        <section v-if="data.currentLease">
          <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Rent schedule') }}</h2>
          <ScheduleList :lines="data.currentLease.schedule" base="/proprietaire" />
        </section>

        <section>
          <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
            <h2 class="font-display text-[22px] text-ink">{{ t('Invoices') }}</h2>
            <Chips v-model="tab" :label="t('Invoices')" :options="[{ value: 'due', label: t('To collect'), count: due.length }, { value: 'paid', label: t('Paid'), count: paid.length }]" />
          </div>
          <InvoiceList v-if="rows.length" :key="tab" :invoices="rows" base="/proprietaire" show-tenant />
          <p v-else class="surface px-5 py-6 text-center text-[14px] text-ink-mute">{{ tab === 'due' ? t('Nothing to collect on this property.') : t('No paid invoice yet.') }}</p>
        </section>

        <section>
          <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Repairs') }}</h2>
          <IssueList v-if="data.issues.length" :issues="data.issues" base="/proprietaire" show-tenant />
          <p v-else class="surface px-5 py-6 text-center text-[14px] text-ink-mute">{{ t('No repair request on this property.') }}</p>
        </section>

        <section>
          <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Past leases') }}</h2>
          <p v-if="!data.pastLeases.length" class="surface px-5 py-6 text-center text-[14px] text-ink-mute">{{ t('No past lease for this property.') }}</p>
          <ul v-else class="stagger surface divide-y divide-line overflow-hidden">
            <Row v-for="l in data.pastLeases" :key="l.id" :to="leaseHref(l.id)">
              <p class="truncate text-[14.5px] font-semibold text-ink">{{ l.tenant.name }}</p>
              <p class="text-[12.5px] text-ink-mute">{{ l.endDate ? t('{0} to {1}', date(l.startDate), date(l.endDate)) : date(l.startDate) }}</p>
              <template #end><StatusBadge kind="lease" :status="l.status" /></template>
            </Row>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Panel from '@/components/Panel.vue'
import IssueList from '@/components/IssueList.vue'
import Facts from '@/components/Facts.vue'
import Row from '@/components/Row.vue'
import Btn from '@/components/Btn.vue'
import Chips from '@/components/Chips.vue'
import Initials from '@/components/Initials.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import LeaseTerms from '@/components/LeaseTerms.vue'
import ScheduleList from '@/components/ScheduleList.vue'
import InvoiceList from '@/components/InvoiceList.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t } from '@/i18n'
import { date, num } from '@/format'

const props = defineProps({ id: String })
const { data, error, reload } = useLoad('get_property', () => ({ name: props.id }))
const leaseHref = (id) => `/proprietaire/baux/${encodeURIComponent(id)}`
const tab = ref('due')
const due = computed(() => (data.value?.invoices || []).filter((i) => i.outstanding > 0))
const paid = computed(() => (data.value?.invoices || []).filter((i) => i.outstanding <= 0))
const rows = computed(() => (tab.value === 'due' ? due.value : paid.value))
const features = computed(() => {
  const f = data.value.features
  return [
    ...(data.value.buildingName ? [{ label: t('Building'), value: data.value.buildingName }] : []),
    ...(f.type ? [{ label: t('Type'), value: f.type }] : []),
    ...(f.bedrooms ? [{ label: t('Bedrooms'), value: num(f.bedrooms) }] : []),
    ...(f.bathrooms ? [{ label: t('Bathrooms'), value: num(f.bathrooms) }] : []),
    ...(f.area ? [{ label: t('Area'), value: `${num(f.area)} m²` }] : []),
    { label: t('Furnished'), value: f.furnished ? t('Yes') : t('No') },
  ]
})
</script>
