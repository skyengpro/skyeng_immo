import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import * as api from '@/data/api';
import type { SessionUser } from '@/data/types';
import { adoptAccountLanguage } from '@/i18n';
import { setCurrency } from '@/lib/format';

// Interface state only: who is signed in. Business data stays behind api.ts.

interface AppState {
  booting: boolean;
  /** The server could not be reached while reading the session. */
  offline: boolean;
  user: SessionUser | null;
  /** Signed in with an account that has no access to the app. */
  noAccess: boolean;
}

interface AppContextValue extends AppState {
  setUser: (user: SessionUser | null) => void;
  /** Reads the session again from the server. */
  refreshSession: () => Promise<void>;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>({ booting: true, offline: false, user: null, noAccess: false });

  const refreshSession = useCallback(async () => {
    try {
      const session = await api.getSession();
      setCurrency(session.currency);
      adoptAccountLanguage(session.user?.language ?? null);
      setState({ booting: false, offline: false, user: session.user, noAccess: session.noAccess });
    } catch {
      setState((current) => ({ ...current, booting: false, offline: current.user === null }));
    }
  }, []);

  useEffect(() => {
    void refreshSession();
    // A 403 means the session ended (signed out elsewhere, expired): read it again.
    return api.onAuthError(() => void refreshSession());
  }, [refreshSession]);

  const setUser = useCallback(
    (user: SessionUser | null) => setState((current) => ({ ...current, user, noAccess: false, offline: false })),
    [],
  );

  const value = useMemo(() => ({ ...state, setUser, refreshSession }), [state, setUser, refreshSession]);
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppState must be used inside AppStateProvider');
  return context;
}
