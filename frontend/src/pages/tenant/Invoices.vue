<template>
  <div>
    <PageHeader :eyebrow="t('Payments')" :title="t('Invoices')" />
    <Chips v-model="tab" class="mb-5" :label="t('Invoices')" :options="[{ value: 'unpaid', label: t('To pay') }, { value: 'paid', label: t('Receipts') }]" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" />
    <EmptyState v-else-if="!data.length" class="surface" :icon="tab === 'paid' ? 'lucide-receipt-text' : 'lucide-circle-check'"
      :title="tab === 'paid' ? t('No receipt yet') : t('Nothing to pay')" :text="tab === 'paid' ? t('Once an invoice is paid, it becomes a receipt you can download here.') : t('Every invoice is paid. Well done.')" />
    <template v-else>
      <div class="mb-3 flex items-baseline justify-between rounded-app px-4 py-3" :class="tab === 'paid' ? 'bg-ok-soft' : 'bg-paper-deep/70'">
        <span class="text-[13.5px] text-ink-soft">{{ tab === 'paid' ? t('Total received') : t('Total to pay') }}</span>
        <span class="font-display text-[22px] text-ink tabular">{{ money(total) }}</span>
      </div>
      <InvoiceList v-if="tab === 'unpaid'" :key="tab" :invoices="data" base="/locataire" />
      <ul v-else class="stagger surface divide-y divide-line overflow-hidden">
        <li v-for="inv in data" :key="inv.id" class="flex items-center gap-3 px-4 py-3.5 md:px-5">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-ok-soft"><span class="lucide-receipt-text size-[18px] text-ok" /></span>
          <RouterLink :to="`/locataire/factures/${encodeURIComponent(inv.id)}`" class="min-w-0 flex-1 hover:underline">
            <p class="text-balance text-[14.5px] font-semibold text-ink">{{ period(inv.periodStart, inv.periodEnd) }}</p>
            <p class="truncate text-[12.5px] text-ink-mute">{{ t('No. {0}', inv.id) }}</p>
          </RouterLink>
          <div class="flex shrink-0 flex-col items-end gap-1">
            <span class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ money(inv.total) }}</span>
            <a :href="downloadUrl('invoice', inv.id)" target="_blank" rel="noopener" class="inline-flex items-center gap-1 rounded-full bg-sky-soft px-2.5 py-1 text-[12px] font-semibold text-sky hover:bg-sky-mid/20">
              <span class="lucide-download size-3.5" />{{ t('Receipt (PDF)') }}
            </a>
          </div>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import Chips from '@/components/Chips.vue'
import InvoiceList from '@/components/InvoiceList.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { downloadUrl, get } from '@/api'
import { t } from '@/i18n'
import { money, period } from '@/format'

const route = useRoute()
const router = useRouter()
const tab = ref(route.query.onglet === 'payees' ? 'paid' : 'unpaid')
const data = ref(null)
const error = ref(null)
const total = computed(() => (data.value || []).reduce((s, i) => s + (tab.value === 'paid' ? i.total : i.outstanding), 0))

async function reload() {
  data.value = null
  error.value = null
  try {
    data.value = await get('list_invoices', { tab: tab.value })
  } catch (e) {
    error.value = e
  }
}
watch(tab, (v) => {
  router.replace({ query: v === 'paid' ? { onglet: 'payees' } : {} })
  reload()
}, { immediate: true })
</script>
