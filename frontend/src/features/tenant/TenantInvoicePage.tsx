import { useParams } from 'react-router';
import { useTranslation } from 'react-i18next';
import { DownloadButton } from '@/components/DownloadButton';
import { DetailLayout, Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { DetailSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import { useApi } from '@/lib/useApi';
import { InvoiceHeaderCard, InvoiceLinesCard, PaymentsSection } from '@/features/shared/InvoiceSections';

export function TenantInvoicePage() {
  const { id = '' } = useParams();
  const { t } = useTranslation();
  const invoice = useApi(() => api.getInvoice(id), [id]);

  return (
    <Page title={t('invoice.title', { number: id })} backTo="/locataire/factures" breadcrumbs={[{ label: t('nav.invoices'), to: '/locataire/factures' }, { label: id }]}>
      <QueryView query={invoice} skeleton={<DetailSkeleton />}>
        {(data) => (
          <DetailLayout
            main={
              <>
                <InvoiceLinesCard invoice={data} />
                <PaymentsSection payments={data.payments} />
              </>
            }
            aside={
              <InvoiceHeaderCard invoice={data}>
                {data.outstanding > 0 && <p className="rounded bg-surface-sidebar p-3 text-ink-gray-8">{t('tenant.home.howToPay')}</p>}
                <div className="flex flex-col gap-2">
                  {data.outstanding <= 0 && data.payments[0] && (
                    <DownloadButton kind="receipt" name={data.payments[0].id} label={t('actions.downloadReceipt')} variant="solid" fullWidth />
                  )}
                  <DownloadButton kind="invoice" name={data.id} label={t('actions.downloadInvoice')} fullWidth />
                </div>
              </InvoiceHeaderCard>
            }
          />
        )}
      </QueryView>
    </Page>
  );
}
