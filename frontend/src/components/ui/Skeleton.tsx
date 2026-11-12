import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/cn';

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden="true" className={cn('animate-pulse rounded bg-surface-gray-2 motion-reduce:animate-none', className)} />;
}

/** Zone en cours de chargement, annoncée aux lecteurs d'écran. */
export function LoadingRegion({ children, className }: { children: React.ReactNode; className?: string }) {
  const { t } = useTranslation();
  return (
    <div role="status" aria-live="polite" className={className}>
      <span className="sr-only">{t('common.loading')}</span>
      {children}
    </div>
  );
}

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="divide-y divide-outline-gray-2 rounded-xl border border-outline-gray-2">
      {Array.from({ length: rows }, (_, index) => (
        <div key={index} className="flex items-center justify-between gap-4 p-4">
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-2/3 max-w-60" />
            <Skeleton className="h-3 w-1/2 max-w-40" />
          </div>
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('space-y-3 rounded-xl border border-outline-gray-2 p-4', className)}>
      <Skeleton className="h-5 w-40" />
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton key={index} className={cn('h-4', index % 2 ? 'w-1/2' : 'w-3/4')} />
      ))}
    </div>
  );
}

/** Squelette d'écran de détail : contenu principal et panneau de synthèse. */
export function DetailSkeleton() {
  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:gap-6">
      <div className="space-y-4">
        <CardSkeleton lines={4} />
        <CardSkeleton lines={3} />
      </div>
      <CardSkeleton lines={4} />
    </div>
  );
}
