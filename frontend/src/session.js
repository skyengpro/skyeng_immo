import { reactive } from 'vue'
import { get, net, clearCache, setCacheUser } from './api'
import { hasSavedLanguage, setLanguage } from './i18n'

const SPACE_KEY = 'sky_immo.space'

export const session = reactive({
  ready: false,
  /** { id, role: 'manager' | 'owner' | 'tenant', spaces: ['owner' | 'tenant'], firstName, fullName, email, language } */
  user: null,
  noAccess: false,
  currency: 'XAF',
  /** The screens shown: 'owner' (landlords, and staff over every property) or 'tenant'. */
  space: null,
})

/** The spaces the signed-in user may open; both for someone who is landlord and tenant. */
export const spaces = () => session.user?.spaces || []
export const space = () => session.space
export const home = () => (space() === 'tenant' ? '/locataire' : '/proprietaire')

// The space chosen last on this device, if the user still has it; else the first one (landlord).
function pickSpace(user) {
  const offered = user?.spaces || []
  let saved = null
  try {
    saved = localStorage.getItem(SPACE_KEY)
  } catch {}
  return offered.includes(saved) ? saved : offered[0] || null
}

/** Open the other space. A full load, so every screen and cached read starts from that space. */
export function switchSpace(target) {
  if (target === space() || !spaces().includes(target)) return
  try {
    localStorage.setItem(SPACE_KEY, target)
  } catch {}
  window.location.href = `/sky-immo${target === 'tenant' ? '/locataire' : '/proprietaire'}`
}

export async function loadSession() {
  try {
    const s = await get('get_session')
    Object.assign(session, { user: s.user, noAccess: !!s.noAccess, currency: s.currency || 'XAF', space: pickSpace(s.user) })
    net.csrf = s.csrfToken
    await setCacheUser(s.user?.id)
    if (s.user?.language && !hasSavedLanguage()) setLanguage(s.user.language, { remember: false })
  } catch {
    session.user = null
    await setCacheUser(null)
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
