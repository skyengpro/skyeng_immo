<template>
  <div>
    <PageHeader :eyebrow="isOwner ? [t('Tenant'), data?.property.displayName].filter(Boolean).join(' · ') : [t('My lease'), building].filter(Boolean).join(' · ')" :title="isOwner ? (data?.tenant.name || t('Tenant')) : (data?.property.name || t('My lease'))" :back="back" :back-label="backLabel" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" tall />
    <template v-else>
      <SectionNav :items="jumps" :label="t('Sections of this page')" />
      <div class="grid grid-cols-[minmax(0,1fr)] gap-4 md:grid-cols-[minmax(0,1fr)_320px] md:items-start md:gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-6">
        <aside class="space-y-4 md:order-2 md:sticky md:top-20">
          <!-- the tenant's name is the page title: the contact card only gives the ways to reach them -->
          <Panel v-if="isOwner" id="contact" :title="t('Contact')" padded>
            <div v-if="data.tenantPhone || data.tenantEmail" class="grid gap-2">
              <Btn v-if="data.tenantPhone" block icon="lucide-phone" :label="data.tenantPhone" :href="`tel:${data.tenantPhone}`" />
              <Btn v-if="data.tenantEmail" block icon="lucide-mail" :label="data.tenantEmail" :href="`mailto:${data.tenantEmail}`" />
            </div>
            <p v-else class="text-[14px] text-ink-mute">{{ t('No phone number or email recorded for this tenant.') }}</p>
          </Panel>
          <PropertyFacts v-if="!isOwner && data.features" id="home" :features="data.features" :building-name="data.buildingName" />
          <LeaseTerms id="lease" :lease="data" />
        </aside>

        <div class="min-w-0 space-y-8 md:order-1">
          <template v-if="isOwner">
            <section id="due">
              <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Still to collect') }}</h2>
              <p v-if="!data.invoicesDue.length" class="surface px-5 py-6 text-center text-[14px] text-ink-mute">{{ t('Nothing to collect for this tenant.') }}</p>
              <template v-else>
                <div class="mb-3 flex items-baseline justify-between rounded-app bg-alert-soft px-4 py-3">
                  <span class="text-[13.5px] text-alert">{{ t('Total to collect') }}</span>
                  <span class="font-display text-[22px] text-alert tabular">{{ money(totalDue) }}</span>
                </div>
                <InvoiceList :invoices="data.invoicesDue" base="/proprietaire" />
              </template>
            </section>
            <section id="payments">
              <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Payments received') }}</h2>
              <PaymentList :payments="data.payments" show-invoice />
            </section>
          </template>
          <section v-else id="schedule">
            <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Rent schedule') }}</h2>
            <ScheduleList :lines="data.schedule" base="/locataire" />
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Panel from '@/components/Panel.vue'
import Btn from '@/components/Btn.vue'
import SectionNav from '@/components/SectionNav.vue'
import LeaseTerms from '@/components/LeaseTerms.vue'
import PropertyFacts from '@/components/PropertyFacts.vue'
import ScheduleList from '@/components/ScheduleList.vue'
import InvoiceList from '@/components/InvoiceList.vue'
import PaymentList from '@/components/PaymentList.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t } from '@/i18n'
import { money } from '@/format'
import { space } from '@/session'

const props = defineProps({ id: String })
const { data, error, reload } = useLoad('get_lease', () => ({ name: props.id }))
const isOwner = space() === 'owner'
// "Building · Unit": the building part, for the page eyebrow
const building = computed(() => {
  const d = data.value?.property
  return d && d.displayName !== d.name ? d.displayName.replace(` · ${d.name}`, '') : ''
})
const totalDue = computed(() => (data.value?.invoicesDue || []).reduce((s, i) => s + i.outstanding, 0))
// phone: jump straight to a section instead of scrolling past the others
const jumps = computed(() =>
  isOwner
    ? [
        { id: 'payments', label: t('Payments received'), icon: 'lucide-banknote', count: data.value?.payments.length },
        { id: 'due', label: t('Still to collect'), icon: 'lucide-hourglass', count: data.value?.invoicesDue.length },
        { id: 'contact', label: t('Contact'), icon: 'lucide-phone' },
      ]
    : [
        ...(data.value?.features ? [{ id: 'home', label: t('The property'), icon: 'lucide-house' }] : []),
        { id: 'lease', label: t('The lease'), icon: 'lucide-file-text' },
        { id: 'schedule', label: t('Rent schedule'), icon: 'lucide-calendar-days' },
      ],
)
const back = computed(() => (isOwner ? (data.value ? `/proprietaire/biens/${encodeURIComponent(data.value.property.id)}` : '/proprietaire/biens') : '/locataire'))
const backLabel = computed(() => (isOwner ? data.value?.property.displayName || t('My properties') : t('Home')))
</script>
