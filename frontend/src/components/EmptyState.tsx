import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';
import { Icon } from './ui/Icon';

interface EmptyStateProps {
  icon: LucideIcon;
  message: ReactNode;
  action?: ReactNode;
}

/** Empty state: a sentence that says what will appear here, with the matching action. */
export function EmptyState({ icon, message, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-4 rounded-xl border border-outline-gray-2 px-6 py-10 text-center">
      <span className="inline-flex size-12 items-center justify-center rounded-full bg-surface-gray-2 text-ink-gray-6">
        <Icon icon={icon} />
      </span>
      <p className="max-w-md text-ink-gray-6">{message}</p>
      {action}
    </div>
  );
}

/** One-line empty message inside a section. */
export function SectionEmpty({ children }: { children: ReactNode }) {
  return <p className="rounded-xl border border-outline-gray-2 p-4 text-ink-gray-6">{children}</p>;
}

/** Titled section of a screen. */
export function Section({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3">
        <h2 className="text-xl font-semibold">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}
