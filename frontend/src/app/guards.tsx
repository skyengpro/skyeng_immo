import { Navigate, Outlet, useLocation } from 'react-router';
import { AppShell } from '@/layouts/AppShell';
import { homePath, spaceOf } from '@/layouts/navigation';
import { useAppState } from './AppStateContext';
import { NoAccessPage, UnauthorizedPage } from './StatusPages';

function useLoginRedirect() {
  const location = useLocation();
  return `/connexion?suite=${encodeURIComponent(location.pathname + location.search)}`;
}

/** Space reserved to some roles: a tenant on /proprietaire/* (or the reverse) sees "Access denied". */
export function RoleSpace({ space }: { space: 'owner' | 'tenant' }) {
  const { user, noAccess } = useAppState();
  const login = useLoginRedirect();
  if (noAccess) return <NoAccessPage />;
  if (!user) return <Navigate to={login} replace />;
  if (spaceOf(user.role) !== space) return <UnauthorizedPage />;
  return <AppShell role={user.role} />;
}

export function RequireAuth() {
  const { user } = useAppState();
  const login = useLoginRedirect();
  return user ? <Outlet /> : <Navigate to={login} replace />;
}

export function IndexRedirect() {
  const { user, noAccess } = useAppState();
  if (noAccess) return <NoAccessPage />;
  return <Navigate to={user ? homePath(user.role) : '/connexion'} replace />;
}
