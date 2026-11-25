// "Install the app" on the home screen. The browser offers it once, early (beforeinstallprompt), so the
// offer is caught here at start and kept for the banner. iPhone never sends it: the banner explains
// Share > Add to Home Screen instead.
import { computed, reactive } from 'vue'

const standalone = () => window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true
const ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
const KEY = 'sky_immo.install.dismissed'

export const install = reactive({
  offer: null,
  installed: standalone(),
  dismissed: (() => {
    try {
      return !!localStorage.getItem(KEY)
    } catch {
      return false
    }
  })(),
  ios,
})

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault()
  install.offer = e
})
window.addEventListener('appinstalled', () => Object.assign(install, { installed: true, offer: null }))

export const showInstall = computed(() => !install.installed && (install.offer || install.ios) && !install.dismissed)

export async function installApp() {
  const offer = install.offer
  if (!offer) return false
  offer.prompt()
  const { outcome } = await offer.userChoice.catch(() => ({ outcome: 'dismissed' }))
  install.offer = null
  if (outcome === 'accepted') install.installed = true
  return outcome === 'accepted'
}

export function dismissInstall() {
  install.dismissed = true
  try {
    localStorage.setItem(KEY, '1')
  } catch {}
}
