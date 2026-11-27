// A page's read: data, loading and error, reloaded when the person comes back to the tab
// (a payment recorded in the desk then shows without reloading the page).
import { onMounted, onUnmounted, ref } from 'vue'
import { get } from './api'

export function useLoad(method, params = () => ({})) {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(true)
  let last = 0

  async function load({ quiet = false } = {}) {
    if (!quiet) loading.value = true
    last = Date.now()
    try {
      data.value = await get(method, params())
      error.value = null
    } catch (e) {
      if (!quiet || !data.value) error.value = e
    } finally {
      loading.value = false
    }
  }
  const onVisible = () => document.visibilityState === 'visible' && Date.now() - last > 30000 && load({ quiet: true })
  onMounted(() => {
    load()
    document.addEventListener('visibilitychange', onVisible)
  })
  onUnmounted(() => document.removeEventListener('visibilitychange', onVisible))
  return { data, error, loading, reload: load }
}
