import { Outlet, ScrollRestoration } from 'react-router';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { ToastProvider } from '@/components/ui/Toast';
import { PublicLayout } from '@/layouts/PublicLayout';
import { AppStateProvider, useAppState } from './AppStateContext';

export function Root() {
  return (
    <AppStateProvider>
      <ToastProvider>
        <RootContent />
      </ToastProvider>
    </AppStateProvider>
  );
}

function RootContent() {
  const { t } = useTranslation();
  const { booting, offline, refreshSession } = useAppState();

  if (booting) {
    return (
      <div className="flex min-h-dvh items-center justify-center gap-2 text-ink-gray-6">
        <Spinner />
        <span>{t('common.loading')}</span>
      </div>
    );
  }

  if (offline) {
    return (
      <PublicLayout>
        <div role="alert" className="space-y-4 text-center">
          <h1 className="text-3xl font-semibold">{t('errors.network.title')}</h1>
          <p className="text-ink-gray-6">{t('errors.network.body')}</p>
          <Button fullWidth onClick={() => void refreshSession()}>
            {t('common.retry')}
          </Button>
        </div>
      </PublicLayout>
    );
  }

  return (
    <>
      <Outlet />
      <ScrollRestoration />
    </>
  );
}
