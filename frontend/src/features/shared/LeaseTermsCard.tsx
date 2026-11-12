import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { DetailList, type DetailItem } from '@/components/DetailList';
import { StatusBadge } from '@/components/StatusBadge';
import { Card } from '@/components/ui/Card';
import type { Deposit, LeaseDetail, LeaseSummary } from '@/data/types';
import { useFormat } from '@/lib/format';

type Lease = LeaseSummary & Partial<Pick<LeaseDetail, 'noticeDays' | 'lines'>> & { deposit?: Deposit | null };

/** Lease terms: dates, payment rhythm, amount per period and its lines, notice, deposit. */
export function LeaseTermsCard({ lease, title, children }: { lease: Lease; title?: string; children?: ReactNode }) {
  const { t } = useTranslation();
  const format = useFormat();
  const items: DetailItem[] = [
    { label: t('lease.start'), value: format.date(lease.startDate) },
    { label: t('lease.end'), value: lease.endDate ? format.date(lease.endDate) : t('lease.noEnd') },
    { label: t('lease.frequency'), value: t(`frequency.${lease.frequency}`) },
    { label: t('lease.perPeriod'), value: <span className="tabular">{format.money(lease.amountPerPeriod)}</span> },
  ];
  if (lease.lines && lease.lines.length > 1) {
    for (const line of lease.lines) {
      items.push({ label: <span className="pl-3">{line.label}</span>, value: <span className="font-medium tabular">{format.money(line.amount)}</span> });
    }
  }
  if (lease.noticeDays) items.push({ label: t('lease.notice'), value: t('lease.noticeDays', { count: lease.noticeDays }) });
  if (lease.deposit) {
    items.push({
      label: t('lease.deposit'),
      value: (
        <span className="inline-flex flex-wrap items-center justify-end gap-2">
          <span className="tabular">{format.money(lease.deposit.amount)}</span>
          {lease.deposit.status !== 'unknown' && <StatusBadge kind="deposit" value={lease.deposit.status} />}
        </span>
      ),
    });
  }

  return (
    <Card title={title ?? t('lease.title')} action={<StatusBadge kind="lease" value={lease.status} />}>
      <div className="space-y-4">
        <DetailList items={items} />
        {children}
      </div>
    </Card>
  );
}
