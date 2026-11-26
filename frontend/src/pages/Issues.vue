<template>
  <div>
    <PageHeader :eyebrow="t('Maintenance')" :title="t('Repairs')"
      :subtitle="isOwner ? t('Approve or reject what your tenants ask for.') : t('Report a problem at home and follow what happens.')">
      <template v-if="!isOwner" #actions>
        <Btn variant="primary" icon="lucide-plus" :label="t('Report a problem')" to="/locataire/maintenance/nouvelle" />
      </template>
    </PageHeader>

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" />
    <EmptyState v-else-if="!data.length" class="surface" icon="lucide-wrench" :title="t('No repair request yet')"
      :text="isOwner ? t('Requests from your tenants appear here, for you to approve.') : t('Something broken at home? Tell us in a minute, with a photo.')">
      <Btn v-if="!isOwner" variant="primary" icon="lucide-plus" :label="t('Report a problem')" to="/locataire/maintenance/nouvelle" />
    </EmptyState>
    <template v-else>
      <div v-if="isOwner && awaiting" class="rise mb-5 flex items-center gap-3 rounded-[16px] border border-warn/20 bg-warn-soft px-4 py-3 text-warn">
        <span class="lucide-hand size-5 shrink-0" />
        <p class="min-w-0 flex-1 text-[13.5px]"><b>{{ tn(awaiting, '{0} request waits for your decision', '{0} requests wait for your decision') }}</b></p>
      </div>
      <Chips v-if="isOwner" v-model="filter" class="mb-5" :label="t('Filter')" :options="options" />
      <IssueList :key="filter" :issues="shown" :base="base" :show-tenant="isOwner" />
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import Btn from '@/components/Btn.vue'
import Chips from '@/components/Chips.vue'
import IssueList from '@/components/IssueList.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { useLoad } from '@/load'
import { t, tn } from '@/i18n'
import { space } from '@/session'

const isOwner = space() === 'owner'
const base = isOwner ? '/proprietaire' : '/locataire'
const { data, error, reload } = useLoad('list_issues', () => ({ space: space() }))
const filter = ref('all')
const STATES = [['awaiting_approval', 'Awaiting approval'], ['in_progress', 'In progress'], ['completed', 'Completed'], ['rejected', 'Rejected']]
const count = (v) => (v === 'all' ? data.value.length : data.value.filter((i) => i.approval === v).length)
const awaiting = computed(() => (data.value ? count('awaiting_approval') : 0))
const options = computed(() => [['all', 'All'], ...STATES].filter(([v]) => v === 'all' || count(v)).map(([value, label]) => ({ value, label: t(label), count: count(value) })))
const shown = computed(() => (data.value || []).filter((i) => filter.value === 'all' || i.approval === filter.value))
// open on what needs a decision, when something does
watch(data, (rows, old) => {
  if (!old && isOwner && rows?.some((i) => i.approval === 'awaiting_approval')) filter.value = 'awaiting_approval'
}, { once: true })
</script>
