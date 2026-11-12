import { LogOut } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAppState } from '@/app/AppStateContext';
import { DetailList } from '@/components/DetailList';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { Page } from '@/components/Page';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useSignOut } from '@/layouts/useSignOut';
import { homePath } from '@/layouts/navigation';

/** EP-01 screen 5: language. Plus who is signed in, and signing out. */
export function AccountPage() {
  const { t } = useTranslation();
  const { user } = useAppState();
  const signOut = useSignOut();
  if (!user) return null;

  return (
    <Page title={t('nav.account')} breadcrumbs={[{ label: t('nav.home'), to: homePath(user.role) }, { label: t('nav.account') }]}>
      <div className="space-y-5 lg:max-w-2xl">
        <Card title={t('account.language')}>
          <div className="space-y-3">
            <LanguageSwitcher variant="long" />
            <p className="text-ink-gray-6">{t('account.languageHint')}</p>
          </div>
        </Card>

        <Card title={t('account.profile')}>
          <DetailList
            items={[
              { label: t('account.name'), value: user.fullName },
              { label: t('auth.email'), value: <span className="break-all">{user.email}</span> },
              { label: t('account.space'), value: t(`roles.${user.role}`) },
            ]}
          />
        </Card>

        <p className="rounded-xl bg-surface-sidebar p-4 text-ink-gray-8">{t(user.role === 'manager' ? 'account.helpManager' : 'account.help')}</p>

        <Button variant="outline" icon={LogOut} onClick={() => void signOut()} fullWidth className="lg:w-auto">
          {t('actions.signOut')}
        </Button>
      </div>
    </Page>
  );
}
