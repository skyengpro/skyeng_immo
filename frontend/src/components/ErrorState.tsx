import { CircleAlert, SearchX } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { ApiError } from '@/data/api';
import { useAppState } from '@/app/AppStateContext';
import { homePath } from '@/layouts/navigation';
import { Button, ButtonLink } from './ui/Button';
import { Icon } from './ui/Icon';

interface ErrorStateProps {
  error: ApiError;
  onRetry: () => void;
}

/** What went wrong, and the one thing to do next. */
export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();
  const { user } = useAppState();
  const notFound = error.kind === 'not_found' || error.kind === 'forbidden';
  return (
    <div role="alert" className="flex flex-col items-center gap-4 rounded-xl border border-outline-gray-2 px-6 py-10 text-center">
      <span className="inline-flex size-12 items-center justify-center rounded-full bg-red-bg text-red-ink">
        <Icon icon={notFound ? SearchX : CircleAlert} />
      </span>
      <div className="max-w-md space-y-1">
        <h2 className="text-xl font-semibold">{notFound ? t('errors.notFound.title') : t('errors.network.title')}</h2>
        <p className="text-ink-gray-6">{notFound ? t('errors.notFound.body') : t('errors.network.body')}</p>
      </div>
      {notFound ? (
        <ButtonLink to={user ? homePath(user.role) : '/connexion'} variant="subtle">
          {t('errors.backHome')}
        </ButtonLink>
      ) : (
        <Button variant="subtle" onClick={onRetry}>
          {t('common.retry')}
        </Button>
      )}
    </div>
  );
}
