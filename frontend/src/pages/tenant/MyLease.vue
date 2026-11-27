<template>
  <div>
    <PageHeader :eyebrow="t('Tenant')" :title="t('My lease')" :subtitle="t('Choose the home you want to see.')" />
    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="2" />
    <EmptyState v-else-if="!data.length" class="surface" icon="lucide-file-text" :title="t('No lease yet')" :text="t('Your lease appears here once your property manager sets it up.')" />
    <ul v-else class="stagger surface divide-y divide-line overflow-hidden">
      <Row v-for="l in data" :key="l.id" :to="`/locataire/bail/${encodeURIComponent(l.id)}`">
        <template #lead><span class="flex size-10 shrink-0 items-center justify-center rounded-full bg-sky-soft"><span class="lucide-house size-[18px] text-sky-mid" /></span></template>
        <p class="truncate text-[15px] font-semibold text-ink">{{ l.property.displayName }}</p>
        <p v-if="unitSummary(l.features)" class="truncate text-[12.5px] text-ink-soft">{{ unitSummary(l.features) }}</p>
        <p class="text-[12.5px] text-ink-mute">{{ l.endDate ? t('{0} to {1}', date(l.startDate), date(l.endDate)) : date(l.startDate) }}</p>
        <template #end>
          <span v-if="l.amountPerPeriod > 0" class="whitespace-nowrap text-[14px] font-semibold text-ink tabular">{{ perPeriod(l.amountPerPeriod, l.frequency) }}</span>
          <StatusBadge kind="lease" :status="l.status" />
        </template>
      </Row>
    </ul>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import Row from '@/components/Row.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t } from '@/i18n'
import { date, perPeriod, unitSummary } from '@/format'

const router = useRouter()
const { data, error, reload } = useLoad('list_my_leases')
// one lease: open it directly
watch(data, (rows) => rows?.length === 1 && router.replace(`/locataire/bail/${encodeURIComponent(rows[0].id)}`))
</script>
