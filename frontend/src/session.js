import { reactive } from 'vue'
import { get, net, clearCache } from './api'
import { hasSavedLanguage, setLanguage } from './i18n'

export const session = reactive({
  ready: false,
  /** { id, role: 'manager' | 'owner' | 'tenant', firstName, fullName, email, language } */
  user: null,
  noAccess: false,
  currency: 'XAF',
})

/** Staff use the landlord screens, over every property. */
export const space = (user = session.user) => (user?.role === 'tenant' ? 'tenant' : 'owner')
export const home = (user = session.user) => (space(user) === 'tenant' ? '/locataire' : '/proprietaire')

export async function loadSession() {
  try {
    const s = await get('get_session')
    Object.assign(session, { user: s.user, noAccess: !!s.noAccess, currency: s.currency || 'XAF' })
    net.csrf = s.csrfToken
    if (s.user?.language && !hasSavedLanguage()) setLanguage(s.user.language, { remember: false })
  } catch {
    session.user = null
  }
  session.ready = true
  return session.user
}

export async function login(usr, pwd) {
  const res = await fetch('/api/method/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ usr, pwd }),
  })
  if (!res.ok) {
    const json = await res.json().catch(() => ({}))
    const error = new Error(json.message || 'Could not sign in.')
    error.status = res.status
    throw error
  }
  await clearCache()
  // reloaded so the session cookie and a fresh CSRF token are used everywhere
  const next = new URLSearchParams(location.search).get('next')
  window.location.href = next?.startsWith('/') && !next.startsWith('//') ? `/sky-immo${next}` : '/sky-immo/'
}

export async function logout() {
  await clearCache()
  try {
    await fetch('/api/method/logout', { method: 'POST', headers: { 'X-Frappe-CSRF-Token': net.csrf || '' } })
  } catch {}
  window.location.href = '/sky-immo/connexion'
}
