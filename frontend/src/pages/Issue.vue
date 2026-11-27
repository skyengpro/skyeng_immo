<template>
  <div>
    <PageHeader :eyebrow="t('Repair request')" :title="data?.title || t('Repair request')" :back="`${base}/maintenance`" :back-label="t('Repairs')" />

    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="2" tall />
    <div v-else class="grid grid-cols-[minmax(0,1fr)] gap-4 md:grid-cols-[minmax(0,1fr)_320px] md:items-start md:gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-6">
      <aside class="space-y-4 md:order-2 md:sticky md:top-20">
        <Panel v-if="data.canDecide" :title="t('Your decision')" padded class="!border-warn/25 !bg-warn-soft/40">
          <p class="mb-4 text-[13.5px] text-ink-soft">{{ t('Only you, as the owner, decide on this repair. Approving sends it to the property manager.') }}</p>
          <div class="grid gap-2">
            <Btn variant="brand" size="lg" block icon="lucide-check" :loading="busy === 'approve'" :disabled="!!busy" :label="t('Approve')" @click="decide('approve')" />
            <Btn size="lg" block icon="lucide-x" :loading="busy === 'reject'" :disabled="!!busy" :label="t('Reject')" @click="decide('reject')" />
          </div>
        </Panel>
        <Panel v-if="data.canComplete" :title="t('Is the work done?')" padded class="!border-ok/25 !bg-ok-soft/40">
          <p class="mb-4 text-[13.5px] text-ink-soft">{{ t('Once the problem is fixed, close the request. Your property manager sees it as resolved.') }}</p>
          <Btn variant="brand" size="lg" block icon="lucide-check-check" :loading="busy === 'complete'" :disabled="!!busy" :label="t('Mark as completed')" @click="complete" />
        </Panel>
        <Panel padded>
          <div class="flex flex-wrap gap-2">
            <StatusBadge kind="approval" :status="data.approval" />
            <span v-if="data.urgent" class="rounded-full bg-alert-soft px-2.5 py-1 text-[12px] font-medium text-alert">{{ t('Urgent') }}</span>
          </div>
          <p class="mt-3 text-[13.5px] text-ink-soft">{{ t(help[data.approval]) }}</p>
          <div class="mt-4"><Facts :items="facts" /></div>
        </Panel>
      </aside>

      <div class="min-w-0 space-y-4 md:order-1">
        <Panel :title="t('What was reported')" padded>
          <p class="whitespace-pre-line text-[14.5px] leading-relaxed text-ink-soft">{{ data.description }}</p>
          <ul v-if="data.photos?.length" class="mt-4 grid gap-3" :class="data.photos.length > 1 && 'sm:grid-cols-2'">
            <li v-for="(p, i) in data.photos" :key="p.id">
              <a :href="photoUrl(data.id, p.id)" target="_blank" rel="noopener">
                <img :src="photoUrl(data.id, p.id)" :alt="t('Photo {0}', i + 1)" loading="lazy" class="max-h-80 w-full rounded-[14px] border border-line object-cover" />
              </a>
            </li>
          </ul>
        </Panel>
        <Panel v-if="data.resolution" :title="t('What was done')" padded>
          <p class="whitespace-pre-line text-[14.5px] leading-relaxed text-ink-soft">{{ data.resolution }}</p>
        </Panel>
        <Panel :title="t('Answers from the property manager')" padded>
          <p v-if="!data.replies.length" class="text-[14px] text-ink-mute">{{ t('No answer yet. It will show here.') }}</p>
          <ul v-else class="space-y-3">
            <li v-for="(r, i) in data.replies" :key="i" class="rounded-[14px] bg-paper-deep/70 p-3.5">
              <div class="mb-1 flex flex-wrap items-baseline justify-between gap-2">
                <span class="text-[13.5px] font-semibold text-ink">{{ r.author }}</span>
                <span class="text-[12px] text-ink-mute">{{ date(r.at, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) }}</span>
              </div>
              <p class="whitespace-pre-line text-[14px] text-ink-soft">{{ r.message }}</p>
            </li>
          </ul>
        </Panel>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { toast } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import Panel from '@/components/Panel.vue'
import Facts from '@/components/Facts.vue'
import Btn from '@/components/Btn.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { photoUrl, post } from '@/api'
import { useLoad } from '@/load'
import { categoryLabel } from '@/issues'
import { t } from '@/i18n'
import { date } from '@/format'
import { space } from '@/session'
import { loadAttention } from '@/attention'

const props = defineProps({ id: String })
const base = space() === 'owner' ? '/proprietaire' : '/locataire'
const { data, error, reload } = useLoad('get_issue', () => ({ name: props.id }))
const busy = ref('')
const help = {
  awaiting_approval: "Waiting for the owner's decision.",
  in_progress: 'Approved. The property manager is taking care of it.',
  rejected: 'The owner did not approve this request.',
  completed: 'The problem is fixed.',
}
const facts = computed(() => {
  const d = data.value
  return [
    { label: t('Request no.'), value: d.id },
    { label: t('Type of problem'), value: t(categoryLabel[d.category] || 'Something else') },
    ...(d.tenantName ? [{ label: t('Tenant'), value: d.tenantName }] : []),
    ...(d.property ? [{ label: t('Unit'), value: d.property.displayName }] : []),
    ...(d.landlordName ? [{ label: t('Owner'), value: d.landlordName }] : []),
    { label: t('Sent on'), value: date(d.createdAt) },
  ]
})

async function complete() {
  busy.value = 'complete'
  try {
    await post('complete_issue', { name: props.id })
    toast.success(t('Request closed. Thank you.'))
    await reload()
  } catch (e) {
    toast.error(e.message)
  } finally {
    busy.value = ''
  }
}

async function decide(decision) {
  busy.value = decision
  try {
    await post('decide_issue', { name: props.id, decision })
    toast.success(decision === 'approve' ? t('Request approved') : t('Request rejected'))
    await reload()
    loadAttention()
  } catch (e) {
    toast.error(e.message)
  } finally {
    busy.value = ''
  }
}
</script>
