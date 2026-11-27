<template>
  <div>
    <div class="rise mb-8 flex flex-wrap items-end justify-between gap-5">
      <div>
        <p class="eyebrow mb-2">{{ longDate(new Date()) }}</p>
        <h1 class="font-display text-[30px] leading-[1.08] text-ink md:text-[44px]">{{ greeting }}, <em class="italic text-sky-mid">{{ session.user.firstName }}</em></h1>
      </div>
      <div class="grid w-full grid-cols-2 gap-2 sm:flex sm:w-auto">
        <Btn icon="lucide-receipt-text" :label="t('My receipts')" to="/locataire/factures?onglet=payees" />
        <Btn variant="primary" icon="lucide-triangle-alert" :label="t('Report a problem')" to="/locataire/maintenance/nouvelle" />
      </div>
    </div>

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="2" tall />
    <div v-else class="grid grid-cols-[minmax(0,1fr)] gap-4 md:grid-cols-2 md:gap-5">
      <!-- the one thing a tenant needs first: how much, by when -->
      <section class="surface rise relative overflow-hidden p-5 md:p-6" :class="late && '!border-alert/30 ring-4 ring-alert-soft'">
        <div class="mb-3 flex items-center justify-between gap-2">
          <h2 class="text-[15px] font-semibold text-ink">{{ t('Next payment') }}</h2>
          <StatusBadge v-if="next" :kind="next.kind === 'invoice' ? 'invoice' : 'schedule'" :status="(next.invoice || next.line).status" />
        </div>
        <p v-if="!next" class="text-[14px] text-ink-mute">{{ t('No payment coming up on your lease.') }}</p>
        <template v-else>
          <p class="whitespace-nowrap font-display text-[34px] min-[420px]:text-[40px] md:text-[30px] lg:text-[38px] xl:text-[44px] leading-none text-ink tabular">{{ money(next.invoice ? next.invoice.outstanding : next.line.amount) }}</p>
          <p class="mt-2 text-[15px]" :class="late ? 'font-semibold text-alert' : 'text-ink-soft'">{{ dueText }}</p>
          <p class="text-[13px] text-ink-mute">{{ period(item.periodStart, item.periodEnd) }}</p>
          <p class="mt-4 rounded-app bg-paper-deep/70 p-3.5 text-[13.5px] text-ink-soft">{{ t('Pay your property manager (cash, bank transfer or Mobile Money). The payment shows here as soon as it is recorded.') }}</p>
          <Btn v-if="next.invoice" class="mt-4" variant="brand" block :label="t('See the invoice')" :to="`/locataire/factures/${encodeURIComponent(next.invoice.id)}`" />
        </template>
      </section>

      <div class="space-y-4 md:space-y-5">
        <RouterLink to="/locataire/factures" class="surface rise group flex items-center justify-between gap-3 p-5 transition hover:-translate-y-0.5 hover:shadow-lift">
          <div class="min-w-0">
            <p class="text-[15px] font-semibold text-ink">{{ t('Total to pay') }}</p>
            <p class="text-[13px] text-ink-mute">{{ data.unpaidCount ? tn(data.unpaidCount, '{0} invoice to pay', '{0} invoices to pay') : t('You are up to date') }}</p>
          </div>
          <span class="flex shrink-0 items-center gap-2">
            <span class="whitespace-nowrap font-display text-[24px] tabular" :class="data.balanceDue ? 'text-alert' : 'text-ok'">{{ money(data.balanceDue) }}</span>
            <span class="lucide-chevron-right size-4 text-ink-faint transition group-hover:translate-x-0.5" />
          </span>
        </RouterLink>

        <RouterLink v-for="h in data.homes" :key="h.leaseId" :to="`/locataire/bail/${encodeURIComponent(h.leaseId)}`" class="surface rise group flex items-center gap-4 p-5 transition hover:-translate-y-0.5 hover:shadow-lift">
          <span class="flex size-12 shrink-0 items-center justify-center rounded-full bg-sky-soft"><span class="lucide-house size-5 text-sky-mid" /></span>
          <span class="min-w-0 flex-1">
            <span class="block text-[12.5px] text-ink-mute">{{ t('My lease') }}</span>
            <span class="block truncate text-[15px] font-semibold text-ink">{{ h.property.name }}</span>
            <span v-if="h.property.displayName !== h.property.name" class="block truncate text-[12.5px] text-ink-soft">{{ h.property.displayName.replace(` · ${h.property.name}`, '') }}</span>
            <span v-if="h.endDate" class="block text-[12.5px] text-ink-mute">{{ t('Lease until {0}', date(h.endDate)) }}</span>
          </span>
          <span class="lucide-chevron-right size-4 text-ink-faint transition group-hover:translate-x-0.5" />
        </RouterLink>

        <Panel :title="t('My latest request')">
          <p v-if="!data.latestIssue" class="px-5 pb-5 text-[14px] text-ink-mute">{{ t('You have not reported any problem.') }}</p>
          <IssueList v-else :issues="[data.latestIssue]" base="/locataire" class="!rounded-none !border-0 !shadow-none" />
        </Panel>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Btn from '@/components/Btn.vue'
import Panel from '@/components/Panel.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import IssueList from '@/components/IssueList.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { date, longDate, money, period } from '@/format'
import { session } from '@/session'

const { data, error, reload } = useLoad('get_tenant_home')
const next = computed(() => data.value?.next)
const item = computed(() => next.value.invoice || next.value.line)
const late = computed(() => next.value?.invoice?.status === 'overdue')
const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? t('Good morning') : h < 18 ? t('Good afternoon') : t('Good evening')
})
const dueText = computed(() => {
  const n = next.value
  if (n.kind === 'schedule') return t('Next due date: {0}', date(n.line.dueDate))
  if (n.invoice.status === 'overdue') return t('Late by {0}, due on {1}', tn(n.invoice.daysLate, '{0} day', '{0} days'), date(n.invoice.dueDate))
  return t('To pay by {0}', date(n.invoice.dueDate))
})
</script>
