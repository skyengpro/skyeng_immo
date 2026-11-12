import { useCallback, useEffect, useRef, useState, type DependencyList } from 'react';
import { ApiError } from '@/data/api';

export type QueryState<T> =
  | { status: 'loading'; data?: undefined; error?: undefined }
  | { status: 'error'; data?: undefined; error: ApiError }
  | { status: 'success'; data: T; error?: undefined };

export type Query<T> = QueryState<T> & { reload: () => void };

/** Do not refetch more often than this when the user comes back to the app. */
const REFRESH_AFTER_MS = 30_000;

function toApiError(error: unknown): ApiError {
  return error instanceof ApiError ? error : new ApiError('network');
}

/**
 * Read through api.ts with loading / error / content states.
 * Data is read again, in the background, when the user comes back to the tab:
 * a payment recorded in the desk then shows without reloading the page.
 */
export function useApi<T>(fetcher: () => Promise<T>, deps: DependencyList): Query<T> {
  const [state, setState] = useState<QueryState<T>>({ status: 'loading' });
  const latest = useRef(0);
  const lastRun = useRef(0);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const run = useCallback((background: boolean) => {
    latest.current += 1;
    lastRun.current = Date.now();
    const request = latest.current;
    if (!background) setState({ status: 'loading' });
    fetcherRef.current().then(
      (data) => {
        if (request === latest.current) setState({ status: 'success', data });
      },
      (error: unknown) => {
        // A failed background refresh keeps what is on screen.
        if (request === latest.current && !background) setState({ status: 'error', error: toApiError(error) });
      },
    );
  }, []);

  useEffect(() => {
    run(false);
    return () => {
      latest.current += 1;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible' && Date.now() - lastRun.current > REFRESH_AFTER_MS) run(true);
    };
    document.addEventListener('visibilitychange', onVisible);
    window.addEventListener('focus', onVisible);
    return () => {
      document.removeEventListener('visibilitychange', onVisible);
      window.removeEventListener('focus', onVisible);
    };
  }, [run]);

  const reload = useCallback(() => run(false), [run]);
  return { ...state, reload };
}
