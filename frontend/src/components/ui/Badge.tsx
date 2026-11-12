import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export type BadgeTone = 'green' | 'orange' | 'red' | 'yellow' | 'blue' | 'gray';

const TONES: Record<BadgeTone, string> = {
  green: 'bg-green-bg text-green-ink',
  orange: 'bg-orange-bg text-orange-ink',
  red: 'bg-red-bg text-red-ink',
  yellow: 'bg-yellow-bg text-yellow-ink',
  blue: 'bg-blue-bg text-blue-ink',
  gray: 'bg-gray-bg text-gray-ink',
};

export function Badge({ tone, children, className }: { tone: BadgeTone; children: ReactNode; className?: string }) {
  return (
    <span className={cn('inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-1 text-sm font-semibold leading-none', TONES[tone], className)}>
      {children}
    </span>
  );
}
