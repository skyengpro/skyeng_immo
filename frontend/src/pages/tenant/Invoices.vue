<template>
  <div>
    <PageHeader :eyebrow="t('Payments')" :title="t('Invoices')" />
    <Chips v-model="tab" class="mb-5" :label="t('Invoices')" :options="[{ value: 'unpaid', label: t('To pay') }, { value: 'paid', label: t('Paid') }]" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" />
    <EmptyState v-else-if="!data.length" class="surface" :icon="tab === 'paid' ? 'lucide-receipt-text' : 'lucide-circle-check'"
      :title="tab === 'paid' ? t('No paid invoice yet') : t('Nothing to pay')" :text="tab === 'paid' ? t('Your paid invoices and receipts appear here.') : t('Every invoice is paid. Well done.')" />
    <template v-else>
      <div class="mb-3 flex items-baseline justify-between rounded-[14px] px-4 py-3" :class="tab === 'paid' ? 'bg-ok-soft' : 'bg-paper-deep/70'">
        <span class="text-[13.5px] text-ink-soft">{{ tab === 'paid' ? t('Total paid') : t('Total to pay') }}</span>
        <span class="font-display text-[22px] text-ink tabular">{{ money(total) }}</span>
      </div>
      <p v-if="tab === 'paid'" class="mb-3 text-[13px] text-ink-mute">{{ t('Open an invoice to download its receipt.') }}</p>
      <InvoiceList :key="tab" :invoices="data" base="/locataire" />
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
import { get } from '@/api'
import { t } from '@/i18n'
import { money } from '@/format'

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
