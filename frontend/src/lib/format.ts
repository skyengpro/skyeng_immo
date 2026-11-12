import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { TFunction } from 'i18next';
import type { ISODate, ISODateTime, Lang } from '@/data/types';
import { parseISODate } from './dates';

const LOCALES: Record<Lang, string> = { fr: 'fr-CM', en: 'en-CM' };

/** Company currency, set once the session is read. XAF / XOF are written "FCFA". */
let currency = 'XAF';
export function setCurrency(code: string) {
  currency = code || 'XAF';
}

export function asLang(value: string | undefined): Lang {
  return value?.startsWith('en') ? 'en' : 'fr';
}

/** Language-dependent formats: "150 000 FCFA" / "150,000 FCFA", "12 nov. 2026" / "12 Nov 2026". */
export function createFormatter(lang: Lang, t: TFunction) {
  const locale = LOCALES[lang];
  const number = new Intl.NumberFormat(locale, { maximumFractionDigits: 0 });
  const shortDate = new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short', year: 'numeric' });
  const longDate = new Intl.DateTimeFormat(locale, { weekday: 'long', day: 'numeric', month: 'long' });
  const time = new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' });

  // en-CM writes "29 Sept 2026": rebuild "29 Sep 2026" with en-US abbreviations.
  const englishParts = new Intl.DateTimeFormat('en-US', { day: 'numeric', month: 'short', year: 'numeric' });

  const toDate = (value: ISODate | ISODateTime) => (value.length > 10 ? new Date(value) : parseISODate(value));
  const date = (value: ISODate | ISODateTime) => {
    if (lang === 'fr') return shortDate.format(toDate(value));
    const parts = Object.fromEntries(englishParts.formatToParts(toDate(value)).map((part) => [part.type, part.value]));
    return `${parts.day} ${parts.month} ${parts.year}`;
  };

  const money = (amount: number) => {
    if (currency === 'XAF' || currency === 'XOF') return `${number.format(amount)} FCFA`;
    try {
      return new Intl.NumberFormat(locale, { style: 'currency', currency, maximumFractionDigits: 0 }).format(amount);
    } catch {
      return `${number.format(amount)} ${currency}`;
    }
  };

  return {
    // Non-breaking space: the amount and "FCFA" stay on one line.
    money,
    number: (value: number) => number.format(value),
    date,
    longDate: (value: ISODate) => longDate.format(toDate(value)),
    dateTime: (value: ISODateTime) => t('format.dateTime', { date: date(value), time: time.format(new Date(value)) }),
    period: (start: ISODate, end: ISODate) => t('format.period', { start: date(start), end: date(end) }),
  };
}

export type Formatter = ReturnType<typeof createFormatter>;

export function useFormat(): Formatter {
  const { t, i18n } = useTranslation();
  const lang = asLang(i18n.language);
  return useMemo(() => createFormatter(lang, t), [lang, t]);
}
