import { lang, t } from './i18n'
import { session } from './session'

const locale = () => (lang.value === 'fr' ? 'fr-FR' : 'en-GB')

export function num(n, digits = 0) {
  return new Intl.NumberFormat(locale(), { maximumFractionDigits: digits }).format(Number(n) || 0)
}

/** "150 000 FCFA": XAF and XOF are written FCFA, as people say it. */
export function money(n) {
  const currency = session.currency || 'XAF'
  if (currency === 'XAF' || currency === 'XOF') return `${num(n)}\u00a0FCFA`
  try {
    return new Intl.NumberFormat(locale(), { style: 'currency', currency, maximumFractionDigits: 0 }).format(Number(n) || 0)
  } catch {
    return `${num(n)} ${currency}`
  }
}

const toDate = (d) => (typeof d === 'string' ? new Date(d.length === 10 ? `${d}T00:00:00` : d.replace(' ', 'T')) : d)

export function date(d, opts = { day: 'numeric', month: 'short', year: 'numeric' }) {
  if (!d) return '—'
  return new Intl.DateTimeFormat(locale(), opts).format(toDate(d))
}

export const shortDate = (d) => date(d, { day: 'numeric', month: 'short' })
export const longDate = (d) => date(d, { weekday: 'long', day: 'numeric', month: 'long' })
export const time = (d) => date(d, { hour: '2-digit', minute: '2-digit' })

/** "November 2026" when the period is exactly one calendar month, else "1 Nov – 15 Dec 2026". */
export function period(start, end) {
  if (!start || !end) return '—'
  const a = toDate(start)
  const b = toDate(end)
  const last = new Date(a.getFullYear(), a.getMonth() + 1, 0).getDate()
  if (a.getDate() === 1 && b.getFullYear() === a.getFullYear() && b.getMonth() === a.getMonth() && b.getDate() === last) {
    const label = date(a, { month: 'long', year: 'numeric' })
    return label.charAt(0).toUpperCase() + label.slice(1)
  }
  return t('{0} to {1}', date(start), date(end))
}

export function today() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/** "per month" label for a Lease frequency. */
export function perPeriod(amount, frequency) {
  const unit = { monthly: '/ month', bimonthly: '/ 2 months', quarterly: '/ 3 months', semiannual: '/ 6 months', annual: '/ year' }[frequency] || '/ month'
  return `${money(amount)} ${t(unit)}`
}
