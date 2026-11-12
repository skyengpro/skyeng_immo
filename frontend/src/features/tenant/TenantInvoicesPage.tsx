import { ReceiptText } from 'lucide-react';
import { useSearchParams } from 'react-router';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/EmptyState';
import { InvoiceRow } from '@/components/InvoiceRow';
import { ListCard } from '@/components/ListCard';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { TotalLine } from '@/components/TotalLine';
import { Segmented } from '@/components/ui/Segmented';
import { ListSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import { useFormat } from '@/lib/format';
import { useApi } from '@/lib/useApi';

type Tab = 'a-payer' | 'payees';

export function TenantInvoicesPage() {
  const { t } = useTranslation();
  const format = useFormat();
  const [params, setParams] = useSearchParams();
  const tab: Tab = params.get('onglet') === 'payees' ? 'payees' : 'a-payer';
  const invoices = useApi(() => api.listInvoices(tab === 'payees' ? 'paid' : 'unpaid'), [tab]);
  const href = (id: string) => `/locataire/factures/${encodeURIComponent(id)}`;

  return (
    <Page title={t('nav.invoices')} breadcrumbs={[{ label: t('nav.home'), to: '/locataire' }, { label: t('nav.invoices') }]}>
      <div className="space-y-4">
        <Segmented
          mode="tabs"
          label={t('nav.invoices')}
          panelId="invoices-panel"
          value={tab}
          fullWidth
          onChange={(value) => setParams(value === 'payees' ? { onglet: 'payees' } : {}, { replace: true })}
          options={[
            { value: 'a-payer', label: t('tenant.invoices.tabs.toPay') },
            { value: 'payees', label: t('tenant.invoices.tabs.paid') },
          ]}
        />
        <div id="invoices-panel" role="tabpanel">
          <QueryView query={invoices} skeleton={<ListSkeleton rows={4} />}>
            {(rows) => {
              if (rows.length === 0) {
                return <EmptyState icon={ReceiptText} message={tab === 'payees' ? t('tenant.invoices.emptyPaid') : t('tenant.invoices.emptyToPay')} />;
              }
              const total = rows.reduce((sum, invoice) => sum + (tab === 'payees' ? invoice.total : invoice.outstanding), 0);
              return (
                <div className="space-y-3">
                  <TotalLine label={t(tab === 'payees' ? 'tenant.invoices.totalPaid' : 'tenant.invoices.totalToPay')} amount={format.money(total)} />
                  {tab === 'payees' && <p className="text-ink-gray-6">{t('tenant.invoices.receiptsHint')}</p>}
                  <ListCard>
                    {rows.map((invoice) => (
                      <InvoiceRow key={invoice.id} invoice={invoice} to={href(invoice.id)} />
                    ))}
                  </ListCard>
                </div>
              );
            }}
          </QueryView>
        </div>
      </div>
    </Page>
  );
}
