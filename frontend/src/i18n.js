// English is written in the code; French comes from fr.js. Missing French keys fall back to English.
import { ref } from 'vue'
import fr from './fr'

const KEY = 'sky_immo.lang'
const saved = (() => {
  try {
    return localStorage.getItem(KEY)
  } catch {
    return null
  }
})()

// Cameroon: French unless the device or the person asks for English
export const lang = ref(saved || ((navigator.language || 'fr').startsWith('en') ? 'en' : 'fr'))
document.documentElement.lang = lang.value

export function setLanguage(code, { remember = true } = {}) {
  lang.value = code && code.startsWith('en') ? 'en' : 'fr'
  document.documentElement.lang = lang.value
  if (!remember) return
  try {
    localStorage.setItem(KEY, lang.value)
  } catch {}
}

export const hasSavedLanguage = () => !!saved

/** Translate, then fill {0}, {1}… with the extra arguments. */
export function t(text, ...args) {
  let out = (lang.value === 'fr' && fr[text]) || text
  args.forEach((a, i) => (out = out.replaceAll(`{${i}}`, a)))
  return out
}

/** Singular or plural, then translated: tn(2, '{0} invoice', '{0} invoices'). */
export function tn(count, one, other) {
  return t(count === 1 ? one : other, count)
}
