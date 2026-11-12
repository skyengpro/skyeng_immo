import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface CardProps {
  title?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  /** Contenu collé aux bords (listes à séparateurs, tableaux). */
  flush?: boolean;
  as?: 'section' | 'div';
}

/** Carte : bordure fine, rayon de 12 px, aucune ombre. */
export function Card({ title, action, children, className, flush, as: Tag = 'section' }: CardProps) {
  return (
    <Tag className={cn('rounded-xl border border-outline-gray-2 bg-surface-base', className)}>
      {(title || action) && (
        <div className={cn('flex flex-wrap items-center justify-between gap-x-3 gap-y-1 px-4 pt-4', flush && 'pb-3')}>
          {title && <h2 className="text-lg font-semibold text-ink-gray-9">{title}</h2>}
          {action}
        </div>
      )}
      <div className={cn(!flush && 'p-4', !flush && (title || action) && 'pt-3')}>{children}</div>
    </Tag>
  );
}
