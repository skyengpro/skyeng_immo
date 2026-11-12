import { Building2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { ListCard, ListRow } from '@/components/ListCard';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { Section, SectionEmpty } from '@/components/EmptyState';
import { StatusBadge } from '@/components/StatusBadge';
import { ButtonLink } from '@/components/ui/Button';
import { CardSkeleton, Skeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { OwnerDashboard } from '@/data/types';
import { today } from '@/lib/dates';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';

function Stat({ label, value, detail, tone }: { label: string; value: string; detail?: string; tone?: 'red' }) {
  return (
    <div className="rounded-xl border border-outline-gray-2 bg-surface-base p-4">
      <p className="text-ink-gray-6">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular lg:text-3xl ${tone === 'red' ? 'text-red-ink' : 'text-ink-gray-9'}`}>{value}</p>
      {detail && <p className="text-ink-gray-6">{detail}</p>}
    </div>
  );
}

function Dashboard({ data }: { data: OwnerDashboard }) {
  const { t } = useTranslation();
  const format = useFormat();
  const { stats } = data;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-semibold">{data.firstName ? t('owner.home.greeting', { name: data.firstName }) : t('owner.home.hello')}</h2>
        <p className="text-lg text-ink-gray-6 first-letter:uppercase">{format.longDate(today())}</p>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        <Stat label={t('owner.home.stats.properties')} value={format.number(stats.properties)} />
        <Stat label={t('owner.home.stats.tenants')} value={format.number(stats.tenants)} />
        <Stat label={t('owner.home.stats.collected')} value={format.money(stats.collectedThisMonth)} />
        <Stat
          label={t('owner.home.stats.unpaid')}
          value={format.money(stats.unpaidTotal)}
          detail={t('owner.home.stats.unpaidCount', { count: stats.unpaidCount })}
          tone={stats.unpaidTotal > 0 ? 'red' : undefined}
        />
      </div>

      <Section title={t('owner.home.overdue')}>
        {data.overdue.length === 0 ? (
          <SectionEmpty>{t('owner.home.overdueEmpty')}</SectionEmpty>
        ) : (
          <ListCard>
            {data.overdue.map((invoice) => (
              // EP-01: an overdue invoice opens the tenant concerned directly.
              <ListRow
                key={invoice.id}
                to={invoice.leaseId ? `/proprietaire/baux/${encodeURIComponent(invoice.leaseId)}` : `/proprietaire/factures/${encodeURIComponent(invoice.id)}`}
              >
                <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
                  <div className="min-w-0">
                    <p className="text-lg font-semibold text-ink-gray-9">{invoice.tenant.name}</p>
                    {invoice.property && <p className="text-ink-gray-6">{invoice.property.displayName}</p>}
                  </div>
                  <p className="text-lg font-semibold text-ink-gray-9 tabular">{format.money(invoice.outstanding)}</p>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <StatusBadge kind="invoice" value="overdue" />
                  <span className="font-semibold text-red-ink">{t('invoice.lateBy', { count: invoice.daysLate })}</span>
                </div>
              </ListRow>
            ))}
          </ListCard>
        )}
      </Section>

      <ButtonLink to="/proprietaire/biens" icon={Building2} fullWidth className="lg:w-auto">
        {t('owner.home.seeProperties')}
      </ButtonLink>
    </div>
  );
}

export function OwnerHomePage() {
  const { t } = useTranslation();
  const dashboard = useApi(() => api.getOwnerDashboard(), []);
  return (
    <Page title={t('nav.home')}>
      <QueryView
        query={dashboard}
        skeleton={
          <div className="space-y-6">
            <Skeleton className="h-9 w-56" />
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
              {[0, 1, 2, 3].map((index) => (
                <CardSkeleton key={index} lines={1} />
              ))}
            </div>
            <CardSkeleton lines={4} />
          </div>
        }
      >
        {(data) => <Dashboard data={data} />}
      </QueryView>
    </Page>
  );
}
