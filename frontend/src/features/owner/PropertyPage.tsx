import { useState } from 'react';
import { useParams } from 'react-router';
import { UserRound } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { DetailList } from '@/components/DetailList';
import { InvoiceRow } from '@/components/InvoiceRow';
import { ListCard, ListRow } from '@/components/ListCard';
import { DetailLayout, Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { Section, SectionEmpty } from '@/components/EmptyState';
import { StatusBadge } from '@/components/StatusBadge';
import { ButtonLink } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Segmented } from '@/components/ui/Segmented';
import { DetailSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { PropertyDetail } from '@/data/types';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';
import { LeaseTermsCard } from '@/features/shared/LeaseTermsCard';
import { ScheduleList } from '@/features/shared/ScheduleList';

const leaseHref = (id: string) => `/proprietaire/baux/${encodeURIComponent(id)}`;
const invoiceHref = (id: string) => `/proprietaire/factures/${encodeURIComponent(id)}`;

function InvoicesSection({ property }: { property: PropertyDetail }) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<'due' | 'paid'>('due');
  const rows = property.invoices.filter((invoice) => (tab === 'due' ? invoice.outstanding > 0 : invoice.outstanding <= 0));
  return (
    <Section title={t('owner.property.invoices')}>
      <Segmented
        mode="tabs"
        label={t('owner.property.invoices')}
        panelId="property-invoices"
        value={tab}
        onChange={setTab}
        options={[
          { value: 'due', label: t('owner.property.tabs.due') },
          { value: 'paid', label: t('owner.property.tabs.paid') },
        ]}
      />
      <div id="property-invoices" role="tabpanel">
        {rows.length === 0 ? (
          <SectionEmpty>{tab === 'due' ? t('owner.property.noDue') : t('owner.property.noPaid')}</SectionEmpty>
        ) : (
          <ListCard>
            {rows.map((invoice) => (
              <InvoiceRow key={invoice.id} invoice={invoice} to={invoiceHref(invoice.id)} showTenant />
            ))}
          </ListCard>
        )}
      </div>
    </Section>
  );
}

function PropertyContent({ property }: { property: PropertyDetail }) {
  const { t } = useTranslation();
  const format = useFormat();
  const current = property.currentLease;
  const { features } = property;

  return (
    <DetailLayout
      aside={
        <>
          <Card>
            <div className="space-y-3">
              <StatusBadge kind="property" value={property.status} />
              <DetailList
                items={[
                  ...(property.buildingName ? [{ label: t('owner.property.building'), value: property.buildingName }] : []),
                  ...(features.type ? [{ label: t('property.type'), value: features.type }] : []),
                  ...(features.bedrooms ? [{ label: t('property.bedrooms'), value: format.number(features.bedrooms) }] : []),
                  ...(features.bathrooms ? [{ label: t('property.bathrooms'), value: format.number(features.bathrooms) }] : []),
                  ...(features.area ? [{ label: t('property.area'), value: t('property.areaValue', { area: format.number(features.area) }) }] : []),
                  { label: t('property.furnished'), value: features.furnished ? t('common.yes') : t('common.no') },
                ]}
              />
            </div>
          </Card>

          {current ? (
            <LeaseTermsCard lease={current} title={t('owner.property.currentLease')}>
              <div className="rounded border border-outline-gray-2 bg-surface-sidebar p-3">
                <p className="text-ink-gray-6">{t('owner.property.tenant')}</p>
                <p className="text-xl font-semibold text-ink-gray-9">{current.tenant.name}</p>
                <p className="text-ink-gray-6">{t('owner.property.moveIn', { date: format.date(current.startDate) })}</p>
              </div>
              <ButtonLink to={leaseHref(current.id)} icon={UserRound} fullWidth>
                {t('owner.property.seeTenant')}
              </ButtonLink>
            </LeaseTermsCard>
          ) : (
            <Card title={t('owner.property.currentLease')}>
              <p className="text-ink-gray-6">{t('owner.property.vacant')}</p>
            </Card>
          )}
        </>
      }
      main={
        <>
          {current && (
            <Section title={t('lease.schedule')}>
              <ScheduleList lines={current.schedule} invoiceHref={invoiceHref} />
            </Section>
          )}

          <InvoicesSection property={property} />

          <Section title={t('owner.property.pastLeases')}>
            {property.pastLeases.length === 0 ? (
              <SectionEmpty>{t('owner.property.noPastLeases')}</SectionEmpty>
            ) : (
              <ListCard>
                {property.pastLeases.map((lease) => (
                  <ListRow key={lease.id} to={leaseHref(lease.id)}>
                    <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
                      <div className="min-w-0">
                        <p className="font-semibold text-ink-gray-9">{lease.tenant.name}</p>
                        <p className="text-ink-gray-6">
                          {lease.endDate ? format.period(lease.startDate, lease.endDate) : format.date(lease.startDate)}
                        </p>
                      </div>
                      <StatusBadge kind="lease" value={lease.status} />
                    </div>
                  </ListRow>
                ))}
              </ListCard>
            )}
          </Section>
        </>
      }
    />
  );
}

export function PropertyPage() {
  const { id = '' } = useParams();
  const { t } = useTranslation();
  const property = useApi(() => api.getProperty(id), [id]);
  const title = property.data?.displayName ?? t('nav.properties');

  return (
    <Page title={title} backTo="/proprietaire/biens" breadcrumbs={[{ label: t('nav.properties'), to: '/proprietaire/biens' }, { label: title }]}>
      <QueryView query={property} skeleton={<DetailSkeleton />}>
        {(data) => <PropertyContent property={data} />}
      </QueryView>
    </Page>
  );
}
