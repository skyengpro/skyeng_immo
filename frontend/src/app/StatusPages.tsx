import { useEffect } from 'react';
import { Lock, SearchX, UserX } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button, ButtonLink } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { PublicLayout } from '@/layouts/PublicLayout';
import { homePath } from '@/layouts/navigation';
import { useSignOut } from '@/layouts/useSignOut';
import { useAppState } from './AppStateContext';

function StatusPage({ kind }: { kind: 'unauthorized' | 'notFound' | 'noAccess' }) {
  const { t } = useTranslation();
  const { user } = useAppState();
  const signOut = useSignOut();
  const title = t(`errors.${kind}.title`);

  useEffect(() => {
    document.title = `${title} · ${t('app.name')}`;
  }, [title, t]);

  return (
    <PublicLayout>
      <div className="flex flex-col items-center gap-4 text-center">
        <span className="inline-flex size-12 items-center justify-center rounded-full bg-surface-gray-2 text-ink-gray-6">
          <Icon icon={kind === 'unauthorized' ? Lock : kind === 'noAccess' ? UserX : SearchX} />
        </span>
        <h1 className="text-3xl font-semibold">{title}</h1>
        <p className="text-ink-gray-6">{t(`errors.${kind}.body`)}</p>
        {kind === 'noAccess' ? (
          <Button fullWidth onClick={() => void signOut()}>
            {t('actions.signOut')}
          </Button>
        ) : (
          <ButtonLink to={user ? homePath(user.role) : '/connexion'} fullWidth>
            {user ? t('errors.backHome') : t('actions.signIn')}
          </ButtonLink>
        )}
      </div>
    </PublicLayout>
  );
}

export function UnauthorizedPage() {
  return <StatusPage kind="unauthorized" />;
}

export function NotFoundPage() {
  return <StatusPage kind="notFound" />;
}

export function NoAccessPage() {
  return <StatusPage kind="noAccess" />;
}
