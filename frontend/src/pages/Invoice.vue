<template>
  <div>
    <PageHeader :eyebrow="t('Invoice {0}', id)" :title="data ? t('Rent · {0}', period(data.periodStart, data.periodEnd)) : t('Invoice')" :back="back" :back-label="isOwner ? t('The tenant') : t('Invoices')" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="2" tall />
    <div v-else class="grid grid-cols-[minmax(0,1fr)] gap-4 md:grid-cols-[minmax(0,1fr)_320px] md:items-start md:gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-6">
      <aside class="space-y-4 md:sticky md:top-20 md:order-2">
        <Panel padded>
          <StatusBadge kind="invoice" :status="data.status" />
          <p class="mt-4 text-[13px] text-ink-mute">{{ left ? t('Still to pay') : t('Amount') }}</p>
          <p class="font-display text-[44px] leading-none text-ink tabular">{{ money(left ? data.outstanding : data.total) }}</p>
          <p v-if="data.status === 'overdue'" class="mt-2 text-[13.5px] font-semibold text-alert">{{ tn(data.daysLate, 'Late by {0} day', 'Late by {0} days') }}</p>
          <div class="mt-5">
            <Facts :items="facts" />
          </div>
          <div class="mt-5 grid gap-2">
            <Btn variant="primary" block icon="lucide-download" :label="t('Download the invoice')" :href="downloadUrl('invoice', data.id)" target="_blank" />
            <Btn v-if="isOwner && data.leaseId" block icon="lucide-user-round" :label="t('See the tenant')" :to="back" />
          </div>
        </Panel>
      </aside>

      <div class="min-w-0 space-y-8 md:order-1">
        <section>
          <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('What is billed') }}</h2>
          <Panel padded>
            <ul class="divide-y divide-line">
              <li v-for="(item, i) in data.items" :key="i" class="flex items-baseline justify-between gap-4 py-2.5 first:pt-0">
                <span class="text-[14px] text-ink-soft">{{ item.label }}</span>
                <span class="whitespace-nowrap text-[14px] font-medium text-ink tabular">{{ money(item.amount) }}</span>
              </li>
            </ul>
            <dl class="mt-3 space-y-1.5 border-t border-line-strong pt-3 text-[14px]">
              <div class="flex justify-between font-semibold text-ink"><dt>{{ t('Total') }}</dt><dd class="tabular">{{ money(data.total) }}</dd></div>
              <div v-if="data.total - data.outstanding > 0" class="flex justify-between text-ink-mute"><dt>{{ t('Already paid') }}</dt><dd class="tabular">{{ money(data.total - data.outstanding) }}</dd></div>
              <div class="flex justify-between font-semibold" :class="left ? 'text-alert' : 'text-ok'"><dt>{{ t('Still to pay') }}</dt><dd class="tabular">{{ money(data.outstanding) }}</dd></div>
            </dl>
          </Panel>
        </section>
        <section>
          <h2 class="mb-3 font-display text-[22px] text-ink">{{ t('Payments') }}</h2>
          <PaymentList :payments="data.payments" />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Panel from '@/components/Panel.vue'
import Facts from '@/components/Facts.vue'
import Btn from '@/components/Btn.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import PaymentList from '@/components/PaymentList.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { downloadUrl } from '@/api'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { date, money, period } from '@/format'
import { space } from '@/session'

const props = defineProps({ id: String })
const { data, error, reload } = useLoad('get_invoice', () => ({ name: props.id }))
const isOwner = space() === 'owner'
const left = computed(() => data.value?.outstanding > 0)
const back = computed(() =>
  isOwner ? (data.value?.leaseId ? `/proprietaire/baux/${encodeURIComponent(data.value.leaseId)}` : '/proprietaire/biens') : '/locataire/factures',
)
const facts = computed(() => [
  { label: t('Number'), value: data.value.id },
  { label: t('Due date'), value: date(data.value.dueDate) },
  { label: t('Period'), value: period(data.value.periodStart, data.value.periodEnd) },
  ...(isOwner ? [{ label: t('Tenant'), value: data.value.tenant.name }] : []),
  ...(data.value.property ? [{ label: t('Unit'), value: data.value.property.displayName }] : []),
])
</script>
