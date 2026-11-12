import { useParams } from 'react-router';
import { useTranslation } from 'react-i18next';
import { DownloadButton } from '@/components/DownloadButton';
import { DetailLayout, Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { ButtonLink } from '@/components/ui/Button';
import { DetailSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import { useApi } from '@/lib/useApi';
import { InvoiceHeaderCard, InvoiceLinesCard, PaymentsSection } from '@/features/shared/InvoiceSections';

export function OwnerInvoicePage() {
  const { id = '' } = useParams();
  const { t } = useTranslation();
  const invoice = useApi(() => api.getInvoice(id), [id]);
  const data = invoice.data;
  const back = data?.leaseId ? `/proprietaire/baux/${encodeURIComponent(data.leaseId)}` : '/proprietaire/biens';

  return (
    <Page title={t('invoice.title', { number: id })} backTo={back} breadcrumbs={[{ label: t('nav.properties'), to: '/proprietaire/biens' }, { label: id }]}>
      <QueryView query={invoice} skeleton={<DetailSkeleton />}>
        {(value) => (
          <DetailLayout
            main={
              <>
                <InvoiceLinesCard invoice={value} />
                <PaymentsSection payments={value.payments} />
              </>
            }
            aside={
              <InvoiceHeaderCard invoice={value}>
                <p className="text-ink-gray-8">{t('owner.invoice.tenant', { name: value.tenant.name })}</p>
                <div className="flex flex-col gap-2">
                  <DownloadButton kind="invoice" name={value.id} label={t('actions.downloadInvoice')} variant="solid" fullWidth />
                  {value.leaseId && (
                    <ButtonLink to={back} variant="subtle" fullWidth>
                      {t('owner.invoice.seeTenant')}
                    </ButtonLink>
                  )}
                </div>
              </InvoiceHeaderCard>
            }
          />
        )}
      </QueryView>
    </Page>
  );
}
