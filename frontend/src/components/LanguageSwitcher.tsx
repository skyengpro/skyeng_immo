import { useTranslation } from 'react-i18next';
import { useAppState } from '@/app/AppStateContext';
import * as api from '@/data/api';
import type { Lang } from '@/data/types';
import { setLanguage } from '@/i18n';
import { asLang } from '@/lib/format';
import { Segmented } from './ui/Segmented';

/** FR / EN switch: changes the language at once, keeps the page. Saved on the account for emails. */
export function LanguageSwitcher({ variant = 'short' }: { variant?: 'short' | 'long' }) {
  const { t, i18n } = useTranslation();
  const { user } = useAppState();
  const options: { value: Lang; label: string; ariaLabel?: string; lang: Lang }[] = (['fr', 'en'] as const).map((lang) => ({
    value: lang,
    label: variant === 'short' ? t(`language.short.${lang}`) : t(`language.${lang}`),
    ariaLabel: variant === 'short' ? t(`language.${lang}`) : undefined,
    lang,
  }));

  function change(lang: Lang) {
    setLanguage(lang);
    // Not blocking: the screen already changed; the account keeps it for the next emails.
    if (user) void api.setLanguage(lang).catch(() => undefined);
  }

  return (
    <Segmented label={t('language.label')} options={options} value={asLang(i18n.language)} onChange={change} fullWidth={variant === 'long'} />
  );
}
