import { Link } from 'react-router';
import { ChevronRight, FileText, ReceiptText, TriangleAlert } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { IssueRow } from '@/components/IssueRow';
import { ListCard } from '@/components/ListCard';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { Section, SectionEmpty } from '@/components/EmptyState';
import { StatusBadge } from '@/components/StatusBadge';
import { ButtonLink } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Icon } from '@/components/ui/Icon';
import { CardSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { TenantHome } from '@/data/types';
import { today } from '@/lib/dates';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';

/** The one thing a tenant needs first: how much, by when. */
function NextPaymentCard({ next }: { next: TenantHome['next'] }) {
  const { t } = useTranslation();
  const format = useFormat();

  if (!next) {
    return (
      <Card title={t('tenant.home.next')}>
        <p className="text-ink-gray-6">{t('tenant.home.noNext')}</p>
      </Card>
    );
  }

  if (next.kind === 'schedule') {
    const { line } = next;
    return (
      <Card title={t('tenant.home.next')} action={<StatusBadge kind="schedule" value={line.status} />}>
        <div className="space-y-1">
          <p className="text-4xl font-semibold text-ink-gray-9 tabular">{format.money(line.amount)}</p>
          <p className="text-lg text-ink-gray-8">{t('tenant.home.upcomingOn', { date: format.date(line.dueDate) })}</p>
          <p className="text-ink-gray-6">{format.period(line.periodStart, line.periodEnd)}</p>
        </div>
      </Card>
    );
  }

  const { invoice } = next;
  const late = invoice.status === 'overdue';
  return (
    <Card title={t('tenant.home.next')} action={<StatusBadge kind="invoice" value={invoice.status} />} className={late ? 'border-red-ink' : undefined}>
      <div className="space-y-4">
        <div className="space-y-1">
          <p className="text-4xl font-semibold text-ink-gray-9 tabular">{format.money(invoice.outstanding)}</p>
          <p className={late ? 'text-lg font-semibold text-red-ink' : 'text-lg text-ink-gray-8'}>
            {late
              ? t('tenant.home.lateBy', { count: invoice.daysLate, date: format.date(invoice.dueDate) })
              : t('tenant.home.dueOn', { date: format.date(invoice.dueDate) })}
          </p>
          <p className="text-ink-gray-6">{format.period(invoice.periodStart, invoice.periodEnd)}</p>
        </div>
        <p className="rounded bg-surface-sidebar p-3 text-ink-gray-8">{t('tenant.home.howToPay')}</p>
        <ButtonLink to={`/locataire/factures/${encodeURIComponent(invoice.id)}`} variant="subtle" fullWidth>
          {t('tenant.home.seeInvoice')}
        </ButtonLink>
      </div>
    </Card>
  );
}

export function TenantHomePage() {
  const { t } = useTranslation();
  const format = useFormat();
  const home = useApi(() => api.getTenantHome(), []);

  return (
    <Page title={t('nav.home')}>
      <QueryView
        query={home}
        skeleton={
          <div className="grid gap-4 lg:grid-cols-2">
            <CardSkeleton lines={4} />
            <CardSkeleton lines={3} />
          </div>
        }
      >
        {(data) => (
          <div className="space-y-6">
            <div>
              <h2 className="text-3xl font-semibold">{data.firstName ? t('tenant.home.greeting', { name: data.firstName }) : t('tenant.home.hello')}</h2>
              <p className="text-lg text-ink-gray-6 first-letter:uppercase">{format.longDate(today())}</p>
            </div>
            <div className="grid gap-4 lg:grid-cols-2 lg:gap-6">
              <div className="space-y-4">
                <NextPaymentCard next={data.next} />
                <Link
                  to={data.unpaidCount > 0 ? '/locataire/factures' : '/locataire/factures?onglet=payees'}
                  className="flex min-h-16 items-center justify-between gap-3 rounded-xl border border-outline-gray-2 p-4 transition-colors hover:bg-surface-sidebar"
                >
                  <span>
                    <span className="block text-lg font-semibold text-ink-gray-9">{t('tenant.home.balance')}</span>
                    <span className="block text-ink-gray-6">
                      {data.unpaidCount > 0 ? t('tenant.home.unpaidCount', { count: data.unpaidCount }) : t('tenant.home.upToDate')}
                    </span>
                  </span>
                  <span className="flex items-center gap-2">
                    <span className={`text-2xl font-semibold tabular ${data.balanceDue > 0 ? 'text-red-ink' : 'text-green-ink'}`}>
                      {format.money(data.balanceDue)}
                    </span>
                    <Icon icon={ChevronRight} className="text-ink-gray-6" />
                  </span>
                </Link>
              </div>

              <div className="space-y-4">
                {data.homes.map((home) => (
                  <Link
                    key={home.leaseId}
                    to={`/locataire/bail/${encodeURIComponent(home.leaseId)}`}
                    className="flex items-start gap-3 rounded-xl border border-outline-gray-2 p-4 transition-colors hover:bg-surface-sidebar"
                  >
                    <span className="inline-flex size-12 shrink-0 items-center justify-center rounded-full bg-surface-gray-2 text-ink-gray-8">
                      <Icon icon={FileText} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-ink-gray-6">{t('nav.myLease')}</span>
                      <span className="block text-lg font-semibold text-ink-gray-9">{home.property.displayName}</span>
                      {home.endDate && <span className="block text-ink-gray-6">{t('tenant.home.leaseEnds', { date: format.date(home.endDate) })}</span>}
                    </span>
                    <Icon icon={ChevronRight} className="mt-3 text-ink-gray-6" />
                  </Link>
                ))}

                <div className="grid gap-3 sm:grid-cols-2">
                  <ButtonLink to="/locataire/maintenance/nouvelle" icon={TriangleAlert} fullWidth>
                    {t('actions.reportIssue')}
                  </ButtonLink>
                  <ButtonLink to="/locataire/factures?onglet=payees" variant="subtle" icon={ReceiptText} fullWidth>
                    {t('tenant.home.receipts')}
                  </ButtonLink>
                </div>

                <Section title={t('tenant.home.latestIssue')}>
                  {data.latestIssue ? (
                    <ListCard>
                      <IssueRow issue={data.latestIssue} to={`/locataire/maintenance/${encodeURIComponent(data.latestIssue.id)}`} />
                    </ListCard>
                  ) : (
                    <SectionEmpty>{t('tenant.home.noIssue')}</SectionEmpty>
                  )}
                </Section>
              </div>
            </div>
          </div>
        )}
      </QueryView>
    </Page>
  );
}
