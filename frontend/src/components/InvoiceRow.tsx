import { useTranslation } from 'react-i18next';
import type { InvoiceSummary } from '@/data/types';
import { useFormat } from '@/lib/format';
import { StatusBadge } from './StatusBadge';
import { ListRow } from './ListCard';

interface InvoiceRowProps {
  invoice: InvoiceSummary;
  to: string;
  /** Landlord view: show who the invoice is for. */
  showTenant?: boolean;
}

/** Invoice row: period (or tenant), amount, what is left to pay, status. */
export function InvoiceRow({ invoice, to, showTenant }: InvoiceRowProps) {
  const { t } = useTranslation();
  const format = useFormat();
  const left = invoice.outstanding > 0;
  return (
    <ListRow to={to}>
      <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
        <p className="min-w-0 font-semibold text-ink-gray-9">
          {showTenant ? invoice.tenant.name : format.period(invoice.periodStart, invoice.periodEnd)}
        </p>
        <StatusBadge kind="invoice" value={invoice.status} />
      </div>
      {showTenant && <p className="text-ink-gray-6">{format.period(invoice.periodStart, invoice.periodEnd)}</p>}
      <p className="mt-1 tabular">
        <span className="text-lg font-semibold text-ink-gray-9">{format.money(left ? invoice.outstanding : invoice.total)}</span>
        <span className="text-ink-gray-6">
          {' · '}
          {left ? t('invoice.dueOn', { date: format.date(invoice.dueDate) }) : t('invoice.number_value', { number: invoice.id })}
        </span>
      </p>
    </ListRow>
  );
}
