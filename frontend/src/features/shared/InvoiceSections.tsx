import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { DetailList } from '@/components/DetailList';
import { DownloadButton } from '@/components/DownloadButton';
import { ListCard, ListRow } from '@/components/ListCard';
import { Section, SectionEmpty } from '@/components/EmptyState';
import { StatusBadge } from '@/components/StatusBadge';
import { Card } from '@/components/ui/Card';
import type { InvoiceDetail, Payment } from '@/data/types';
import { useFormat } from '@/lib/format';

/** Invoice header: status, what is left to pay in large type, number, due date, period, home. */
export function InvoiceHeaderCard({ invoice, children }: { invoice: InvoiceDetail; children?: ReactNode }) {
  const { t } = useTranslation();
  const format = useFormat();
  const left = invoice.outstanding > 0;
  return (
    <Card>
      <div className="space-y-4">
        <div className="space-y-2">
          <StatusBadge kind="invoice" value={invoice.status} />
          <p className="text-ink-gray-6">{left ? t('invoice.outstanding') : t('invoice.amount')}</p>
          <p className="text-4xl font-semibold text-ink-gray-9 tabular">{format.money(left ? invoice.outstanding : invoice.total)}</p>
          {invoice.status === 'overdue' && (
            <p className="font-semibold text-red-ink">{t('invoice.lateBy', { count: invoice.daysLate })}</p>
          )}
        </div>
        <DetailList
          items={[
            { label: t('invoice.number'), value: <span className="tabular">{invoice.id}</span> },
            { label: t('invoice.dueDate'), value: format.date(invoice.dueDate) },
            { label: t('invoice.period'), value: format.period(invoice.periodStart, invoice.periodEnd) },
            ...(invoice.property ? [{ label: t('invoice.property'), value: invoice.property.displayName }] : []),
          ]}
        />
        {children}
      </div>
    </Card>
  );
}

export function InvoiceLinesCard({ invoice }: { invoice: InvoiceDetail }) {
  const { t } = useTranslation();
  const format = useFormat();
  const paid = invoice.total - invoice.outstanding;
  return (
    <Card title={t('invoice.lines')}>
      <table className="w-full text-left">
        <caption className="sr-only">{t('invoice.lines')}</caption>
        <tbody>
          {invoice.items.map((item, index) => (
            <tr key={index} className="border-b border-outline-gray-2">
              <th scope="row" className="py-3 font-normal text-ink-gray-8">
                {item.label}
              </th>
              <td className="py-3 text-right font-medium tabular">{format.money(item.amount)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="font-semibold text-ink-gray-9">
            <th scope="row" className="pt-3 font-semibold">
              {t('invoice.total')}
            </th>
            <td className="pt-3 text-right tabular">{format.money(invoice.total)}</td>
          </tr>
          {paid > 0 && (
            <tr className="text-ink-gray-6">
              <th scope="row" className="pt-1 font-normal">
                {t('invoice.paid')}
              </th>
              <td className="pt-1 text-right tabular">{format.money(paid)}</td>
            </tr>
          )}
          <tr className="text-ink-gray-9">
            <th scope="row" className="pt-1 font-semibold">
              {t('invoice.outstanding')}
            </th>
            <td className="pt-1 text-right font-semibold tabular">{format.money(invoice.outstanding)}</td>
          </tr>
        </tfoot>
      </table>
    </Card>
  );
}

/** One payment: date, amount, how it was paid, receipt download. */
export function PaymentRow({ payment, showInvoice }: { payment: Payment; showInvoice?: boolean }) {
  const { t } = useTranslation();
  const format = useFormat();
  const how = [payment.mode, payment.reference].filter(Boolean).join(' · ');
  return (
    <ListRow>
      <div className="space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
          <div className="min-w-0">
            <p className="font-semibold text-ink-gray-9">{t('invoice.paidOn', { date: format.date(payment.date) })}</p>
            {how && <p className="text-ink-gray-6">{how}</p>}
            {showInvoice && <p className="text-ink-gray-6">{t('invoice.number_value', { number: payment.invoiceId })}</p>}
          </div>
          <p className="text-lg font-semibold tabular">{format.money(payment.amount)}</p>
        </div>
        <DownloadButton kind="receipt" name={payment.id} label={t('actions.downloadReceipt')} />
      </div>
    </ListRow>
  );
}

export function PaymentsSection({ payments, title, showInvoice }: { payments: Payment[]; title?: string; showInvoice?: boolean }) {
  const { t } = useTranslation();
  return (
    <Section title={title ?? t('invoice.payments')}>
      {payments.length === 0 ? (
        <SectionEmpty>{t('invoice.noPayments')}</SectionEmpty>
      ) : (
        <ListCard>
          {payments.map((payment) => (
            <PaymentRow key={`${payment.id}-${payment.invoiceId}`} payment={payment} showInvoice={showInvoice} />
          ))}
        </ListCard>
      )}
    </Section>
  );
}
