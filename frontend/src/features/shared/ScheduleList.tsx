import { useState } from 'react';
import { CalendarDays } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/EmptyState';
import { ListCard, ListRow } from '@/components/ListCard';
import { StatusBadge } from '@/components/StatusBadge';
import { Button } from '@/components/ui/Button';
import type { ScheduleLine } from '@/data/types';
import { useFormat } from '@/lib/format';

const PREVIEW = 6;

/** Rent schedule, line by line, with each line's status. Long schedules show the nearest lines first. */
export function ScheduleList({ lines, invoiceHref }: { lines: ScheduleLine[]; invoiceHref: (id: string) => string }) {
  const { t } = useTranslation();
  const format = useFormat();
  const [all, setAll] = useState(false);

  if (lines.length === 0) return <EmptyState icon={CalendarDays} message={t('lease.scheduleEmpty')} />;

  // Start at the first line still to pay (or to come), keep the two before it for context.
  const firstOpen = lines.findIndex((line) => line.status !== 'paid');
  const start = all ? 0 : Math.max(0, (firstOpen === -1 ? lines.length - PREVIEW : firstOpen) - 2);
  const visible = all ? lines : lines.slice(start, start + PREVIEW);
  const hidden = lines.length - visible.length;

  return (
    <div className="space-y-3">
      <ListCard label={t('lease.schedule')}>
        {visible.map((line) => (
          <ListRow key={line.id} to={line.invoiceId ? invoiceHref(line.invoiceId) : undefined}>
            <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
              <p className="min-w-0 font-semibold text-ink-gray-9">{format.period(line.periodStart, line.periodEnd)}</p>
              <StatusBadge kind="schedule" value={line.status} />
            </div>
            <div className="mt-1 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
              <p className="text-ink-gray-6">
                {line.status === 'upcoming' ? t('lease.notInvoiced') : t('lease.dueOn', { date: format.date(line.dueDate) })}
              </p>
              <span className="text-lg font-semibold tabular">{format.money(line.amount)}</span>
            </div>
          </ListRow>
        ))}
      </ListCard>
      {hidden > 0 && (
        <Button variant="subtle" fullWidth onClick={() => setAll(true)}>
          {t('lease.showAll', { count: lines.length })}
        </Button>
      )}
    </div>
  );
}
