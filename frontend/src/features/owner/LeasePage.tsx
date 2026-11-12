import { useParams } from 'react-router';
import { Mail, Phone } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { InvoiceRow } from '@/components/InvoiceRow';
import { ListCard } from '@/components/ListCard';
import { DetailLayout, Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { Section, SectionEmpty } from '@/components/EmptyState';
import { TotalLine } from '@/components/TotalLine';
import { Card } from '@/components/ui/Card';
import { Icon } from '@/components/ui/Icon';
import { DetailSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { LeaseDetail } from '@/data/types';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';
import { PaymentsSection } from '@/features/shared/InvoiceSections';
import { LeaseTermsCard } from '@/features/shared/LeaseTermsCard';

/** EP-01 landlord screen 4, "Tenant": lease terms, payments, invoices still due, downloads. */
function TenantContent({ lease }: { lease: LeaseDetail }) {
  const { t } = useTranslation();
  const format = useFormat();
  const due = lease.invoicesDue.reduce((sum, invoice) => sum + invoice.outstanding, 0);

  return (
    <DetailLayout
      aside={
        <>
          <Card title={t('owner.lease.tenant')}>
            <div className="space-y-3">
              <p className="text-xl font-semibold text-ink-gray-9">{lease.tenant.name}</p>
              <p className="text-ink-gray-6">{lease.property.displayName}</p>
              {lease.tenantPhone && (
                <a href={`tel:${lease.tenantPhone}`} className="flex min-h-12 items-center gap-2 rounded font-semibold text-link underline underline-offset-2">
                  <Icon icon={Phone} />
                  <span className="tabular">{lease.tenantPhone}</span>
                </a>
              )}
              {lease.tenantEmail && (
                <a href={`mailto:${lease.tenantEmail}`} className="flex min-h-12 items-center gap-2 break-all rounded font-semibold text-link underline underline-offset-2">
                  <Icon icon={Mail} />
                  {lease.tenantEmail}
                </a>
              )}
            </div>
          </Card>
          <LeaseTermsCard lease={lease} />
        </>
      }
      main={
        <>
          <Section title={t('owner.lease.due')}>
            {lease.invoicesDue.length === 0 ? (
              <SectionEmpty>{t('owner.lease.noDue')}</SectionEmpty>
            ) : (
              <div className="space-y-3">
                <TotalLine label={t('owner.lease.totalDue')} amount={format.money(due)} />
                <ListCard>
                  {lease.invoicesDue.map((invoice) => (
                    <InvoiceRow key={invoice.id} invoice={invoice} to={`/proprietaire/factures/${encodeURIComponent(invoice.id)}`} />
                  ))}
                </ListCard>
              </div>
            )}
          </Section>
          <PaymentsSection payments={lease.payments} title={t('owner.lease.payments')} showInvoice />
        </>
      }
    />
  );
}

export function LeasePage() {
  const { id = '' } = useParams();
  const { t } = useTranslation();
  const lease = useApi(() => api.getLease(id), [id]);
  const data = lease.data;
  const title = data ? data.tenant.name : t('owner.lease.tenant');
  const back = data ? `/proprietaire/biens/${encodeURIComponent(data.property.id)}` : '/proprietaire/biens';

  return (
    <Page
      title={title}
      backTo={back}
      breadcrumbs={[
        { label: t('nav.properties'), to: '/proprietaire/biens' },
        ...(data ? [{ label: data.property.displayName, to: back }] : []),
        { label: title },
      ]}
    >
      <QueryView query={lease} skeleton={<DetailSkeleton />}>
        {(value) => <TenantContent lease={value} />}
      </QueryView>
    </Page>
  );
}
