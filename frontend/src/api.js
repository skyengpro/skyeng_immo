// Talks to skyeng_immo.sky_immo.api on the same site.
//
// Reads: every answer is kept on the device (IndexedDB, offline/store.js). With no connection, or a
// very slow one, the last answer is shown and `net.stale` says so. Writes (a decision on a repair, a
// new request, the language) need the server: they fail with OfflineError when it cannot be reached.

import { reactive } from 'vue'
import { cache } from './offline/store'
import { t } from './i18n'

const APP = 'skyeng_immo.sky_immo.api.'
const READ_TIMEOUT = 15000
const WRITE_TIMEOUT = 25000

export const net = reactive({
  online: navigator.onLine,
  csrf: null,
  /** The screen shows a copy kept on the device, not a fresh answer. */
  stale: false,
  freshAt: 0,
})
window.addEventListener('online', () => (net.online = true))
window.addEventListener('offline', () => (net.online = false))

export class ApiError extends Error {
  constructor(message, status, type) {
    super(message)
    this.status = status
    this.type = type
  }
}
export class OfflineError extends Error {
  constructor() {
    super(t('You are offline. This needs a connection, please try again when you are back online.'))
  }
}

const methodUrl = (method) => `/api/method/${method.includes('.') ? method : APP + method}`

/** Frappe's error, as one sentence a person can read. */
function readError(json, status) {
  let message = ''
  try {
    const messages = JSON.parse(json._server_messages || '[]').map((m) => JSON.parse(m).message)
    message = messages.join(' ')
  } catch {}
  message = (message || json.message || json.exception || '').replace(/<[^>]+>/g, '').replace(/^[\w.]+Error: /, '')
  if (status === 403 && !message) message = t('You do not have access to this page.')
  if (status === 404 && !message) message = t('Not found')
  return message || t('Something went wrong. Please try again.')
}

async function request(url, options, timeout) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)
  let res
  try {
    res = await fetch(url, { credentials: 'same-origin', ...options, signal: controller.signal })
  } catch {
    throw new OfflineError()
  } finally {
    clearTimeout(timer)
  }
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new ApiError(readError(json, res.status), res.status, json.exc_type)
  return json.message
}

// Whose answers the device cache holds. Every entry is keyed by that user, so a copy kept for one
// account is never shown to the next one, whichever way they signed in (this app, the desk,
// an invitation link, a password reset). Nothing is read or written before the session is known.
const OWNER_KEY = '__owner'
let cacheUser = null

/** Called once the signed-in user is known: drops the copies kept for anyone else. */
export async function setCacheUser(user) {
  cacheUser = user || null
  if (!cacheUser) return
  if ((await cache.get(OWNER_KEY)) !== cacheUser) {
    await cache.clear()
    await cache.set(OWNER_KEY, cacheUser)
  }
}

const cacheKey = (method, url) => (cacheUser && method !== 'get_session' ? `${cacheUser}|${url}` : null)

export async function get(method, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')).toString()
  const url = methodUrl(method) + (query ? `?${query}` : '')
  try {
    const data = await request(url, { headers: { Accept: 'application/json' } }, READ_TIMEOUT)
    net.stale = false
    net.freshAt = Date.now()
    const key = cacheKey(method, url)
    if (key) cache.set(key, data)
    return data
  } catch (e) {
    const key = cacheKey(method, url)
    if (e instanceof OfflineError && key) {
      const kept = await cache.get(key)
      if (kept !== undefined) {
        net.stale = true
        return kept
      }
    }
    throw e
  }
}

export async function post(method, data = {}) {
  if (!navigator.onLine) throw new OfflineError()
  return request(
    methodUrl(method),
    {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': net.csrf || '' },
      body: JSON.stringify(data),
    },
    WRITE_TIMEOUT,
  )
}

/** PDF of an invoice or a receipt (Payment Entry), from the ERPNext print format. */
export const downloadUrl = (kind, name) => `${methodUrl('download')}?${new URLSearchParams({ kind, name })}`
/** Photo of a repair request, served only to someone who can see that request. */
export const photoUrl = (name, file) => `${methodUrl('issue_photo')}?${new URLSearchParams(file ? { name, file } : { name })}`
export const clearCache = () => cache.clear()
