import { useEffect, useState, type FormEvent } from 'react';
import { Link, Navigate, useSearchParams } from 'react-router';
import { useTranslation } from 'react-i18next';
import { useAppState } from '@/app/AppStateContext';
import { Button } from '@/components/ui/Button';
import { TextField } from '@/components/ui/Field';
import * as api from '@/data/api';
import type { SessionUser } from '@/data/types';
import { PublicLayout } from '@/layouts/PublicLayout';
import { homePath, routeSpace, spaceOf } from '@/layouts/navigation';

/** After sign-in: the page asked for if this account may open it, else the account's home. */
export function destinationFor(user: SessionUser, requested: string | null): string {
  if (requested?.startsWith('/') && !requested.startsWith('//')) {
    const space = routeSpace(requested.split('?')[0]);
    if (space === null || space === spaceOf(user.role)) return requested;
  }
  return homePath(user.role);
}

export function LoginPage() {
  const { t } = useTranslation();
  const { user, noAccess, setUser, refreshSession } = useAppState();
  const [params] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    document.title = `${t('auth.login.title')} · ${t('app.name')}`;
  }, [t]);

  if (user) return <Navigate to={destinationFor(user, params.get('suite'))} replace />;
  if (noAccess) return <Navigate to="/" replace />;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!email.trim() || !password) {
      setError(t('auth.login.missing'));
      return;
    }
    setError(null);
    setPending(true);
    try {
      const session = await api.login(email, password);
      if (session.user) setUser(session.user);
      else await refreshSession();
    } catch (caught) {
      setError(caught instanceof api.ApiError && caught.kind === 'invalid_credentials' ? t('auth.login.invalid') : t('errors.action'));
      setPending(false);
    }
  }

  return (
    <PublicLayout>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold">{t('auth.login.title')}</h1>
          <p className="text-ink-gray-6">{t('auth.login.subtitle')}</p>
        </div>

        <form onSubmit={onSubmit} noValidate className="space-y-5">
          <TextField
            label={t('auth.email')}
            type="email"
            autoComplete="username"
            inputMode="email"
            autoCapitalize="none"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <TextField
            label={t('auth.password')}
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          {error && (
            <p role="alert" className="rounded bg-red-bg px-3 py-2 font-semibold text-red-ink">
              {error}
            </p>
          )}
          <Button type="submit" fullWidth loading={pending}>
            {t('actions.signIn')}
          </Button>
          <div className="text-center">
            <Link to="/mot-de-passe-oublie" className="inline-flex min-h-12 items-center rounded font-semibold text-link underline underline-offset-2">
              {t('auth.login.forgot')}
            </Link>
          </div>
        </form>

        <p className="rounded-xl bg-surface-sidebar p-4 text-ink-gray-6">{t('auth.login.help')}</p>
      </div>
    </PublicLayout>
  );
}
