import { useRef, useState, type ChangeEvent, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { Camera, Droplets, Hammer, KeyRound, Paintbrush, Snowflake, Trash2, Zap, type LucideIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { Button, ButtonLink } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { TextArea, TextField } from '@/components/ui/Field';
import { Icon } from '@/components/ui/Icon';
import { Segmented } from '@/components/ui/Segmented';
import { CardSkeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/components/ui/Toast';
import * as api from '@/data/api';
import type { IssueCategory, TenantHome } from '@/data/types';
import { cn } from '@/lib/cn';
import { downscaleImage } from '@/lib/image';
import { useApi } from '@/lib/useApi';

const CATEGORIES: { value: IssueCategory; icon: LucideIcon }[] = [
  { value: 'plumbing', icon: Droplets },
  { value: 'electricity', icon: Zap },
  { value: 'locksmith', icon: KeyRound },
  { value: 'air_conditioning', icon: Snowflake },
  { value: 'painting', icon: Paintbrush },
  { value: 'other', icon: Hammer },
];

function Step({ number, title, children }: { number: number; title: string; children: React.ReactNode }) {
  return (
    <fieldset className="space-y-3">
      <legend className="mb-3 flex items-center gap-3 text-xl font-semibold text-ink-gray-9">
        <span aria-hidden="true" className="inline-flex size-9 items-center justify-center rounded-full bg-primary text-lg text-primary-text">
          {number}
        </span>
        {title}
      </legend>
      {children}
    </fieldset>
  );
}

function IssueForm({ homes }: { homes: TenantHome['homes'] }) {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  const fileInput = useRef<HTMLInputElement>(null);
  const [property, setProperty] = useState<string | null>(homes.length === 1 ? homes[0].property.id : null);
  const [category, setCategory] = useState<IssueCategory | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [urgent, setUrgent] = useState<'no' | 'yes'>('no');
  const [photo, setPhoto] = useState<string | null>(null);
  const [errors, setErrors] = useState<{ property?: string; category?: string; title?: string; description?: string; photo?: string }>({});
  const [pending, setPending] = useState(false);
  let step = 0;

  async function onPhoto(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    try {
      setPhoto(await downscaleImage(file));
      setErrors((current) => ({ ...current, photo: undefined }));
    } catch {
      setErrors((current) => ({ ...current, photo: t('tenant.newIssue.photoError') }));
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const next = {
      property: property ? undefined : t('tenant.newIssue.homeRequired'),
      category: category ? undefined : t('tenant.newIssue.categoryRequired'),
      title: title.trim() ? undefined : t('tenant.newIssue.titleRequired'),
      description: description.trim() ? undefined : t('tenant.newIssue.descriptionRequired'),
    };
    setErrors(next);
    if (next.property || next.category || next.title || next.description) {
      toast.error(t('tenant.newIssue.checkForm'));
      return;
    }
    setPending(true);
    try {
      const { id } = await api.createIssue({ category: category ?? 'other', title, description, urgent: urgent === 'yes', property, photo });
      toast.success(t('toast.issueSent'));
      navigate(`/locataire/maintenance/${encodeURIComponent(id)}`, { replace: true });
    } catch (error) {
      toast.error(error instanceof api.ApiError && error.serverMessage ? error.serverMessage : t('errors.action'));
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-8 lg:max-w-2xl">
      {homes.length > 1 && (
        <Step number={++step} title={t('tenant.newIssue.which')}>
          <div className="grid gap-2">
            {homes.map((home) => (
              <label
                key={home.property.id}
                className={cn(
                  'flex min-h-14 cursor-pointer items-center gap-3 rounded-xl border-2 px-4 py-3 text-lg has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-ink-gray-8',
                  property === home.property.id ? 'border-primary bg-surface-gray-2 font-semibold' : 'border-outline-gray-2',
                )}
              >
                <input type="radio" name="home" checked={property === home.property.id} onChange={() => setProperty(home.property.id)} className="size-5 accent-[#171717]" />
                {home.property.displayName}
              </label>
            ))}
          </div>
          {errors.property && <p className="font-semibold text-red-ink">{errors.property}</p>}
        </Step>
      )}

      <Step number={++step} title={t('tenant.newIssue.what')}>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
          {CATEGORIES.map(({ value, icon }) => (
            <label
              key={value}
              className={cn(
                'flex min-h-20 cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border-2 px-2 py-3 text-center text-lg transition-colors has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-ink-gray-8',
                category === value ? 'border-primary bg-surface-gray-2 font-semibold text-ink-gray-9' : 'border-outline-gray-2 text-ink-gray-8 hover:border-outline-gray-3',
              )}
            >
              <input type="radio" name="category" value={value} checked={category === value} onChange={() => setCategory(value)} className="sr-only" />
              <Icon icon={icon} size={28} />
              {t(`issueCategory.${value}`)}
            </label>
          ))}
        </div>
        {errors.category && <p className="font-semibold text-red-ink">{errors.category}</p>}
      </Step>

      <Step number={++step} title={t('tenant.newIssue.describe')}>
        <div className="space-y-5">
          <TextField
            label={t('tenant.newIssue.titleLabel')}
            required
            maxLength={120}
            value={title}
            error={errors.title}
            placeholder={t('tenant.newIssue.titlePlaceholder')}
            onChange={(event) => setTitle(event.target.value)}
          />
          <TextArea
            label={t('tenant.newIssue.descriptionLabel')}
            required
            value={description}
            error={errors.description}
            placeholder={t('tenant.newIssue.descriptionPlaceholder')}
            onChange={(event) => setDescription(event.target.value)}
          />
          <div className="space-y-2">
            <p className="font-semibold text-ink-gray-9">{t('tenant.newIssue.urgentQuestion')}</p>
            <Segmented
              label={t('tenant.newIssue.urgentQuestion')}
              value={urgent}
              onChange={setUrgent}
              fullWidth
              options={[
                { value: 'no', label: t('common.no') },
                { value: 'yes', label: t('tenant.newIssue.urgentYes') },
              ]}
            />
            <p className="text-ink-gray-6">{t('tenant.newIssue.urgentHint')}</p>
          </div>
        </div>
      </Step>

      <Step number={++step} title={t('tenant.newIssue.photo')}>
        <input ref={fileInput} type="file" accept="image/*" onChange={(event) => void onPhoto(event)} className="sr-only" aria-label={t('tenant.newIssue.addPhoto')} tabIndex={-1} />
        {photo ? (
          <div className="space-y-3">
            <img src={photo} alt={t('tenant.newIssue.photoPreview')} className="max-h-72 w-full rounded-xl border border-outline-gray-2 object-cover" />
            <div className="grid gap-2 sm:grid-cols-2">
              <Button variant="subtle" icon={Camera} onClick={() => fileInput.current?.click()}>
                {t('tenant.newIssue.changePhoto')}
              </Button>
              <Button variant="outline" icon={Trash2} onClick={() => setPhoto(null)}>
                {t('tenant.newIssue.removePhoto')}
              </Button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            className="flex min-h-28 w-full flex-col items-center justify-center gap-1 rounded-xl border-2 border-dashed border-outline-gray-3 bg-surface-sidebar px-4 py-4 text-ink-gray-6 hover:border-ink-gray-5"
          >
            <Icon icon={Camera} size={32} />
            <span className="text-lg font-semibold text-ink-gray-9">{t('tenant.newIssue.addPhoto')}</span>
            <span>{t('tenant.newIssue.photoHint')}</span>
          </button>
        )}
        {errors.photo && <p className="font-semibold text-red-ink">{errors.photo}</p>}
      </Step>

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button type="submit" loading={pending} fullWidth className="sm:w-auto">
          {t('tenant.newIssue.submit')}
        </Button>
        <ButtonLink to="/locataire/maintenance" variant="ghost" fullWidth className="sm:w-auto">
          {t('common.cancel')}
        </ButtonLink>
      </div>
    </form>
  );
}

export function NewIssuePage() {
  const { t } = useTranslation();
  // The homes come from the tenant's current leases.
  const home = useApi(() => api.getTenantHome(), []);
  return (
    <Page
      title={t('actions.reportIssue')}
      backTo="/locataire/maintenance"
      breadcrumbs={[{ label: t('nav.maintenance'), to: '/locataire/maintenance' }, { label: t('actions.reportIssue') }]}
    >
      <QueryView query={home} skeleton={<CardSkeleton lines={5} className="lg:max-w-2xl" />}>
        {(data) =>
          data.homes.length === 0 ? (
            <Card>
              <p className="text-ink-gray-6">{t('tenant.newIssue.noHome')}</p>
            </Card>
          ) : (
            <IssueForm homes={data.homes} />
          )
        }
      </QueryView>
    </Page>
  );
}
