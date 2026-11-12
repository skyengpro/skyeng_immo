import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

/** Public pages (sign-in, forgot password): app name, FR / EN switch top right. */
export function PublicLayout({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  return (
    <div className="pt-safe flex min-h-dvh flex-col">
      <header className="flex items-center justify-between gap-4 px-4 py-3 lg:px-8 lg:py-5">
        <span className="text-2xl font-semibold text-ink-gray-9">{t('app.name')}</span>
        <LanguageSwitcher />
      </header>
      <main className="flex flex-1 justify-center px-4 pb-16 pt-6 lg:items-center lg:pt-0">
        <div className="w-full max-w-[440px]">{children}</div>
      </main>
    </div>
  );
}
