import type { ReactNode } from 'react';
import { Link } from 'react-router';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Icon } from './ui/Icon';

/** Rows separated by a rule, inside a card. */
export function ListCard({ children, className, label }: { children: ReactNode; className?: string; label?: string }) {
  return (
    <ul aria-label={label} className={cn('divide-y divide-outline-gray-2 overflow-hidden rounded-xl border border-outline-gray-2 bg-surface-base', className)}>
      {children}
    </ul>
  );
}

/** A row that opens a detail (the whole row is the link), or a plain row. */
export function ListRow({ to, children, chevron = true }: { to?: string; children: ReactNode; chevron?: boolean }) {
  const content = (
    <>
      <div className="min-w-0 flex-1">{children}</div>
      {to && chevron && <Icon icon={ChevronRight} className="text-ink-gray-6" />}
    </>
  );
  return (
    <li>
      {to ? (
        <Link to={to} className="flex min-h-16 items-center gap-3 px-4 py-4 transition-colors hover:bg-surface-sidebar active:bg-surface-gray-2">
          {content}
        </Link>
      ) : (
        <div className="flex min-h-16 items-center gap-3 px-4 py-4">{content}</div>
      )}
    </li>
  );
}
