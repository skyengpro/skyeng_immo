import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import type { Lang } from '@/data/types';
import { asLang } from '@/lib/format';
import { readStorage, writeStorage } from '@/lib/storage';
import en from './en.json';
import fr from './fr.json';

const STORAGE_KEY = 'mon-immo:lang';

// Both files must have exactly the same keys: the compiler checks it.
const enMatchesFr: typeof fr = en;
const frMatchesEn: typeof en = fr;

declare module 'i18next' {
  interface CustomTypeOptions {
    resources: { translation: typeof fr };
  }
}

/** Remembered language, else the browser's if French or English, else French. */
function initialLanguage(): Lang {
  const stored = readStorage(STORAGE_KEY);
  if (stored === 'fr' || stored === 'en') return stored;
  const browser = navigator.languages.map((language) => language.slice(0, 2)).find((code) => code === 'fr' || code === 'en');
  return browser ?? 'fr';
}

const lng = initialLanguage();
document.documentElement.lang = lng;

void i18n.use(initReactI18next).init({
  resources: { fr: { translation: frMatchesEn }, en: { translation: enMatchesFr } },
  lng,
  fallbackLng: false,
  interpolation: { escapeValue: false },
  returnNull: false,
});

export function setLanguage(lang: Lang) {
  writeStorage(STORAGE_KEY, lang);
  document.documentElement.lang = lang;
  void i18n.changeLanguage(lang);
}

/** The account's language wins on first sign-in on a device, so emails and screens match. */
export function adoptAccountLanguage(lang: Lang | null) {
  if (lang && !readStorage(STORAGE_KEY)) setLanguage(lang);
}

// Keeps several tabs in the same language.
window.addEventListener('storage', (event) => {
  if (event.key === STORAGE_KEY && event.newValue) {
    const lang = asLang(event.newValue);
    document.documentElement.lang = lang;
    void i18n.changeLanguage(lang);
  }
});

export default i18n;
