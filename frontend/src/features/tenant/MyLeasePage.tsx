import { Navigate, useParams } from 'react-router';
import { FileText } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { EmptyState, Section } from '@/components/EmptyState';
import { ListCard, ListRow } from '@/components/ListCard';
import { DetailLayout, Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { StatusBadge } from '@/components/StatusBadge';
import { DetailSkeleton, ListSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { LeaseDetail, LeaseSummary } from '@/data/types';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';
import { LeaseTermsCard } from '@/features/shared/LeaseTermsCard';
import { ScheduleList } from '@/features/shared/ScheduleList';

const leaseHref = (id: string) => `/locataire/bail/${encodeURIComponent(id)}`;

/** Several leases (several homes, or past ones): pick one. One lease: open it directly. */
function LeaseChooser({ leases }: { leases: LeaseSummary[] }) {
  const { t } = useTranslation();
  const format = useFormat();
  if (leases.length === 0) return <EmptyState icon={FileText} message={t('tenant.lease.empty')} />;
  if (leases.length === 1) return <Navigate to={leaseHref(leases[0].id)} replace />;
  return (
    <div className="space-y-3">
      <p className="text-ink-gray-6">{t('tenant.lease.choose')}</p>
      <ListCard>
        {leases.map((lease) => (
          <ListRow key={lease.id} to={leaseHref(lease.id)}>
            <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
              <div className="min-w-0">
                <p className="text-lg font-semibold text-ink-gray-9">{lease.property.displayName}</p>
                <p className="text-ink-gray-6">{lease.endDate ? format.period(lease.startDate, lease.endDate) : format.date(lease.startDate)}</p>
              </div>
              <StatusBadge kind="lease" value={lease.status} />
            </div>
          </ListRow>
        ))}
      </ListCard>
    </div>
  );
}

function LeaseContent({ lease }: { lease: LeaseDetail }) {
  const { t } = useTranslation();
  return (
    <div className="space-y-4 lg:space-y-6">
      <h2 className="text-2xl font-semibold">{lease.property.displayName}</h2>
      <DetailLayout
      aside={<LeaseTermsCard lease={lease} />}
      main={
        <Section title={t('lease.schedule')}>
          <ScheduleList lines={lease.schedule} invoiceHref={(id) => `/locataire/factures/${encodeURIComponent(id)}`} />
        </Section>
      }
      />
    </div>
  );
}

export function MyLeasePage() {
  const { id } = useParams();
  const { t } = useTranslation();
  const leases = useApi(() => api.listMyLeases(), []);
  const lease = useApi(() => (id ? api.getLease(id) : Promise.resolve(null)), [id]);
  const several = (leases.data?.length ?? 0) > 1;
  const title = t('nav.myLease');

  return (
    <Page
      title={title}
      backTo={id && several ? '/locataire/bail' : undefined}
      breadcrumbs={[
        { label: t('nav.home'), to: '/locataire' },
        { label: t('nav.myLease'), to: id && several ? '/locataire/bail' : undefined },
        ...(id && lease.data && several ? [{ label: lease.data.property.displayName }] : []),
      ]}
    >
      {id ? (
        <QueryView query={lease} skeleton={<DetailSkeleton />}>
          {(value) => (value ? <LeaseContent lease={value} /> : null)}
        </QueryView>
      ) : (
        <QueryView query={leases} skeleton={<ListSkeleton rows={2} />}>
          {(value) => <LeaseChooser leases={value} />}
        </QueryView>
      )}
    </Page>
  );
}
