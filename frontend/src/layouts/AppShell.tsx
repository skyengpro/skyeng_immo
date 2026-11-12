import { Link, Outlet, useLocation } from 'react-router';
import { LogOut } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useAppState } from '@/app/AppStateContext';
import { Icon } from '@/components/ui/Icon';
import type { Role } from '@/data/types';
import { cn } from '@/lib/cn';
import { homePath, isNavActive, navigationFor } from './navigation';
import { useSignOut } from './useSignOut';

/** Signed-in frame: sidebar on the web, tab bar with text labels on a phone. */
export function AppShell({ role }: { role: Role }) {
  return (
    <div className="min-h-dvh">
      <Sidebar role={role} />
      <main className="pb-[calc(theme(spacing.tabbar)+env(safe-area-inset-bottom)+24px)] pt-[calc(theme(spacing.topbar)+env(safe-area-inset-top))] lg:pb-16 lg:pl-sidebar lg:pt-0">
        <div className="mx-auto max-w-content px-4 lg:px-10">
          <Outlet />
        </div>
      </main>
      <TabBar role={role} />
    </div>
  );
}

function Sidebar({ role }: { role: Role }) {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const { user } = useAppState();
  const signOut = useSignOut();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-sidebar flex-col border-r border-outline-gray-2 bg-surface-sidebar lg:flex print:hidden">
      <div className="px-5 pb-4 pt-6">
        <Link to={homePath(role)} className="rounded text-2xl font-semibold text-ink-gray-9">
          {t('app.name')}
        </Link>
      </div>
      <nav aria-label={t('nav.main')} className="flex-1 overflow-y-auto px-3">
        <ul className="space-y-1">
          {navigationFor(role).map((item) => {
            const active = isNavActive(item, pathname);
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'flex min-h-12 items-center gap-3 rounded px-3 py-2 text-lg transition-colors',
                    active
                      ? 'bg-surface-base font-semibold text-ink-gray-9 ring-1 ring-outline-gray-3'
                      : 'font-medium text-ink-gray-8 hover:bg-surface-gray-3',
                  )}
                >
                  <Icon icon={item.icon} className={active ? 'text-ink-gray-9' : 'text-ink-gray-6'} />
                  {t(item.label)}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      {user && (
        <div className="space-y-2 border-t border-outline-gray-2 px-5 py-4">
          <div className="min-w-0">
            <p className="truncate font-semibold text-ink-gray-9">{user.fullName}</p>
            <p className="text-ink-gray-6">{t(`roles.${role}`)}</p>
          </div>
          <button
            type="button"
            onClick={() => void signOut()}
            className="-mx-2 flex min-h-11 items-center gap-2 rounded px-2 font-medium text-ink-gray-8 hover:bg-surface-gray-3"
          >
            <Icon icon={LogOut} className="text-ink-gray-6" />
            {t('actions.signOut')}
          </button>
        </div>
      )}
    </aside>
  );
}

function TabBar({ role }: { role: Role }) {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const items = navigationFor(role);
  return (
    <nav aria-label={t('nav.main')} className="pb-safe fixed inset-x-0 bottom-0 z-30 border-t border-outline-gray-3 bg-surface-base lg:hidden print:hidden">
      <ul className={cn('grid', items.length === 3 ? 'grid-cols-3' : 'grid-cols-5')}>
        {items.map((item) => {
          const active = isNavActive(item, pathname);
          return (
            <li key={item.to}>
              <Link
                to={item.to}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'relative flex min-h-tabbar flex-col items-center justify-center gap-1 px-0.5 py-2 text-center text-xs leading-tight',
                  active ? 'font-bold text-ink-gray-9' : 'font-medium text-ink-gray-6',
                )}
              >
                {active && <span aria-hidden="true" className="absolute inset-x-3 top-0 h-1 rounded-b bg-primary" />}
                <Icon icon={item.icon} size={24} />
                <span>{t(item.label)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
