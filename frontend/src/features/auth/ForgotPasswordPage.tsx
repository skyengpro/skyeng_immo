import { useEffect, useState, type FormEvent } from 'react';
import { MailCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button, ButtonLink } from '@/components/ui/Button';
import { TextField } from '@/components/ui/Field';
import { Icon } from '@/components/ui/Icon';
import * as api from '@/data/api';
import { PublicLayout } from '@/layouts/PublicLayout';

/** Sends Frappe's reset email. The link in it leads to "choose a password", then back to the app. */
export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    document.title = `${t('auth.forgot.title')} · ${t('app.name')}`;
  }, [t]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) {
      setError(t('auth.forgot.invalidEmail'));
      return;
    }
    setError(null);
    setPending(true);
    try {
      await api.requestPasswordReset(email);
      setSent(true);
    } catch {
      setError(t('errors.action'));
    } finally {
      setPending(false);
    }
  }

  return (
    <PublicLayout>
      {sent ? (
        <div role="status" className="space-y-5 text-center">
          <span className="mx-auto inline-flex size-14 items-center justify-center rounded-full bg-green-bg text-green-ink">
            <Icon icon={MailCheck} size={28} />
          </span>
          <h1 className="text-3xl font-semibold">{t('auth.forgot.sentTitle')}</h1>
          <p className="text-ink-gray-6">{t('auth.forgot.sent', { email: email.trim() })}</p>
          <ButtonLink to="/connexion" fullWidth variant="subtle">
            {t('auth.forgot.back')}
          </ButtonLink>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold">{t('auth.forgot.title')}</h1>
            <p className="text-ink-gray-6">{t('auth.forgot.intro')}</p>
          </div>
          <form onSubmit={onSubmit} noValidate className="space-y-5">
            <TextField
              label={t('auth.email')}
              type="email"
              autoComplete="email"
              inputMode="email"
              autoCapitalize="none"
              required
              error={error}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
            <Button type="submit" fullWidth loading={pending}>
              {t('auth.forgot.submit')}
            </Button>
            <ButtonLink to="/connexion" fullWidth variant="ghost">
              {t('auth.forgot.back')}
            </ButtonLink>
          </form>
        </div>
      )}
    </PublicLayout>
  );
}
