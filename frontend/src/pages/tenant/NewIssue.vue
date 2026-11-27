<template>
  <div>
    <PageHeader :eyebrow="t('Repairs')" :title="t('Report a problem')" :back="'/locataire/maintenance'" :back-label="t('Repairs')" />
    <ErrorState v-if="error" :error="error" @retry="reload" />
    <Skeleton v-else-if="!data" :rows="3" tall />
    <EmptyState v-else-if="!data.homes.length" class="surface" icon="lucide-house" :title="t('No home on your lease')" :text="t('You need a running lease to report a problem.')" />
    <form v-else class="mx-auto max-w-2xl space-y-9 md:mx-0" novalidate @submit.prevent="submit">
      <fieldset v-if="data.homes.length > 1" class="space-y-3">
        <legend class="mb-3 flex items-center gap-3 font-display text-[22px] text-ink"><span class="step">1</span>{{ t('Which home?') }}</legend>
        <label v-for="h in data.homes" :key="h.property.id" class="surface flex min-h-14 cursor-pointer items-center gap-3 px-4 py-3 text-[15px] has-[:checked]:border-sky-mid has-[:checked]:bg-sky-mist">
          <input v-model="property" type="radio" name="home" :value="h.property.id" class="size-4 accent-[rgb(var(--si-sky-mid))]" />{{ h.property.displayName }}
        </label>
        <p v-if="errors.property" class="text-[13px] font-semibold text-alert">{{ errors.property }}</p>
      </fieldset>

      <fieldset class="space-y-3">
        <legend class="mb-3 flex items-center gap-3 font-display text-[22px] text-ink"><span class="step">{{ data.homes.length > 1 ? 2 : 1 }}</span>{{ t('What is wrong?') }}</legend>
        <div class="grid grid-cols-2 gap-3 md:grid-cols-3">
          <label v-for="c in categories" :key="c" class="surface flex min-h-[88px] cursor-pointer flex-col items-center justify-center gap-1.5 px-2 py-3 text-center text-[14px] font-medium text-ink-soft transition has-[:checked]:border-sky-mid has-[:checked]:bg-sky-mist has-[:checked]:text-sky">
            <input v-model="category" type="radio" name="category" :value="c" class="sr-only" />
            <span :class="categoryIcon[c]" class="size-6" />{{ t(categoryLabel[c]) }}
          </label>
        </div>
        <p v-if="errors.category" class="text-[13px] font-semibold text-alert">{{ errors.category }}</p>
      </fieldset>

      <fieldset class="space-y-5">
        <legend class="mb-3 flex items-center gap-3 font-display text-[22px] text-ink"><span class="step">{{ data.homes.length > 1 ? 3 : 2 }}</span>{{ t('Describe it') }}</legend>
        <label class="block">
          <span class="mb-1.5 block text-[13px] font-semibold text-ink">{{ t('What is the problem?') }}</span>
          <textarea v-model="description" rows="5" class="field h-auto py-3" :placeholder="t('Example: water is leaking under the kitchen sink since yesterday. Where exactly? Anything we should know?')" />
          <span v-if="errors.description" class="mt-1 block text-[13px] font-semibold text-alert">{{ errors.description }}</span>
        </label>
        <label class="surface flex cursor-pointer items-start gap-3 p-4 has-[:checked]:border-alert/40 has-[:checked]:bg-alert-soft">
          <input v-model="urgent" type="checkbox" class="mt-0.5 size-4 accent-[rgb(var(--si-alert))]" />
          <span><span class="block text-[14.5px] font-semibold text-ink">{{ t('This is urgent') }}</span><span class="block text-[12.5px] text-ink-mute">{{ t('Only for water leaks, no electricity, a door that will not lock…') }}</span></span>
        </label>
      </fieldset>

      <fieldset class="space-y-3">
        <legend class="mb-3 flex items-center gap-3 font-display text-[22px] text-ink"><span class="step">{{ data.homes.length > 1 ? 4 : 3 }}</span>{{ t('Add photos') }} <span class="text-[13px] font-normal text-ink-mute">({{ t('optional') }})</span></legend>
        <input ref="file" type="file" accept="image/*" multiple class="sr-only" tabindex="-1" :aria-label="t('Add a photo')" @change="onPhotos" />
        <ul v-if="photos.length" class="grid grid-cols-2 gap-3">
          <li v-for="(p, i) in photos" :key="i" class="relative overflow-hidden rounded-[14px] border border-line">
            <img :src="p" :alt="t('Photo {0}', i + 1)" class="aspect-[4/3] w-full object-cover" />
            <button type="button" class="absolute right-2 top-2 flex size-8 items-center justify-center rounded-full bg-ink/80 text-on-ink backdrop-blur hover:bg-ink" :aria-label="t('Remove photo {0}', i + 1)" @click="photos.splice(i, 1)">
              <span class="lucide-x size-4" />
            </button>
          </li>
        </ul>
        <button v-if="photos.length < MAX_PHOTOS" type="button" class="flex min-h-28 w-full flex-col items-center justify-center gap-1 rounded-[18px] border-2 border-dashed border-line-strong bg-card/60 px-4 py-4 text-ink-mute transition hover:border-sky-mid hover:text-sky" @click="file.click()">
          <span class="lucide-camera size-7" />
          <span class="text-[15px] font-semibold text-ink">{{ photos.length ? t('Add another photo') : t('Take or choose a photo') }}</span>
          <span class="text-[12.5px]">{{ t('Up to {0} photos, images only, 5 MB each.', MAX_PHOTOS) }}</span>
        </button>
        <p v-if="errors.photo" class="text-[13px] font-semibold text-alert">{{ errors.photo }}</p>
      </fieldset>

      <div class="flex flex-col gap-3 sm:flex-row">
        <Btn type="submit" variant="primary" size="lg" :loading="pending" :label="t('Send the request')" class="sm:min-w-[200px]" />
        <Btn size="lg" variant="ghost" :label="t('Cancel')" to="/locataire/maintenance" />
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import Btn from '@/components/Btn.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import Skeleton from '@/components/Skeleton.vue'
import { post } from '@/api'
import { useLoad } from '@/load'
import { categories, categoryIcon, categoryLabel } from '@/issues'
import { t } from '@/i18n'

const router = useRouter()
// the homes come from the tenant's current leases
const { data, error, reload } = useLoad('get_tenant_home')
const file = ref(null)
const property = ref(null)
const category = ref(null)
const description = ref('')
const urgent = ref(false)
const photos = ref([])
const MAX_PHOTOS = 2
const errors = ref({})
const pending = ref(false)
watch(data, (d) => d?.homes.length === 1 && (property.value = d.homes[0].property.id))

/** Shrinks a phone photo before upload: smaller request, faster on a weak connection. */
function downscale(f, max = 1600) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(f)
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, max / Math.max(img.width, img.height))
      const c = document.createElement('canvas')
      c.width = Math.round(img.width * scale)
      c.height = Math.round(img.height * scale)
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height)
      URL.revokeObjectURL(url)
      resolve(c.toDataURL('image/jpeg', 0.82))
    }
    img.onerror = () => (URL.revokeObjectURL(url), reject(new Error('image')))
    img.src = url
  })
}
async function onPhotos(e) {
  const files = [...(e.target.files || [])]
  e.target.value = ''
  errors.value = { ...errors.value, photo: '' }
  for (const f of files) {
    if (photos.value.length >= MAX_PHOTOS) {
      errors.value = { ...errors.value, photo: t('You can add up to {0} photos.', MAX_PHOTOS) }
      break
    }
    if (!f.type.startsWith('image/')) {
      errors.value = { ...errors.value, photo: t('"{0}" is not an image. Only photos are accepted.', f.name) }
      continue
    }
    try {
      photos.value.push(await downscale(f))
    } catch {
      errors.value = { ...errors.value, photo: t('This photo could not be read. Try another one.') }
    }
  }
}

async function submit() {
  errors.value = {
    property: property.value ? '' : t('Choose the home concerned.'),
    category: category.value ? '' : t('Choose what is wrong.'),
    description: description.value.trim() ? '' : t('Describe the problem.'),
  }
  if (Object.values(errors.value).some(Boolean)) return toast.error(t('Please check the form.'))
  pending.value = true
  try {
    const { id } = await post('create_issue', { category: category.value, description: description.value, urgent: urgent.value ? 1 : 0, property: property.value, photos: photos.value })
    toast.success(t('Request sent'))
    router.replace(`/locataire/maintenance/${encodeURIComponent(id)}`)
  } catch (e) {
    toast.error(e.message)
    pending.value = false
  }
}
</script>

<style scoped>
.step {
  @apply flex size-8 shrink-0 items-center justify-center rounded-full bg-ink font-sans text-[14px] font-semibold text-on-ink;
}
</style>
