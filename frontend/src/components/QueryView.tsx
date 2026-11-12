import type { ReactNode } from 'react';
import type { Query } from '@/lib/useApi';
import { ErrorState } from './ErrorState';
import { LoadingRegion } from './ui/Skeleton';

interface QueryViewProps<T> {
  query: Query<T>;
  skeleton: ReactNode;
  children: (data: T) => ReactNode;
}

/** Affiche le squelette, l'erreur ou le contenu d'une lecture. */
export function QueryView<T>({ query, skeleton, children }: QueryViewProps<T>) {
  if (query.status === 'loading') return <LoadingRegion>{skeleton}</LoadingRegion>;
  if (query.status === 'error') return <ErrorState error={query.error} onRetry={query.reload} />;
  return <>{children(query.data)}</>;
}
