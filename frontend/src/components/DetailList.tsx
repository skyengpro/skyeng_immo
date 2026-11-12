import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface DetailItem {
  label: ReactNode;
  value: ReactNode;
}

/** Label / value pairs: label on the left, value on the right, one per line. */
export function DetailList({ items, columns = 1 }: { items: DetailItem[]; columns?: 1 | 2 }) {
  return (
    <dl className={cn('grid gap-x-8 gap-y-3', columns === 2 && 'lg:grid-cols-2')}>
      {items.map((item, index) => (
        <div key={index} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-0.5">
          <dt className="text-ink-gray-6">{item.label}</dt>
          <dd className="text-right font-semibold text-ink-gray-9">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
