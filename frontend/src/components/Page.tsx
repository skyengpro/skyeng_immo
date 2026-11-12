import { useEffect, type ReactNode } from 'react';
import { Link } from 'react-router';
import { ArrowLeft, ChevronRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/cn';
import { Icon } from './ui/Icon';

export interface Crumb {
  label: string;
  to?: string;
}

interface PageProps {
  title: string;
  /** Écran de détail : bouton retour dans la barre supérieure mobile. */
  backTo?: string;
  breadcrumbs?: Crumb[];
  /** Actions de l'en-tête web. */
  actions?: ReactNode;
  /** Action contextuelle à droite de la barre supérieure mobile. */
  mobileAction?: ReactNode;
  children: ReactNode;
}

/** Barre supérieure fixe sur mobile ; titre et fil d'Ariane sur le web. */
export function Page({ title, backTo, breadcrumbs = [], actions, mobileAction, children }: PageProps) {
  const { t } = useTranslation();

  useEffect(() => {
    document.title = `${title} · ${t('app.name')}`;
  }, [title, t]);

  return (
    <>
      <header className="pt-safe fixed inset-x-0 top-0 z-30 border-b border-outline-gray-2 bg-surface-base lg:hidden print:hidden">
        <div className="flex min-h-topbar items-center gap-1 px-2">
          {backTo ? (
            <Link
              to={backTo}
              className="inline-flex min-h-12 shrink-0 items-center gap-1 rounded px-2 font-semibold text-ink-gray-9 hover:bg-surface-gray-2"
            >
              <Icon icon={ArrowLeft} />
              {t('common.back')}
            </Link>
          ) : (
            <span className="w-2 shrink-0" />
          )}
          <h1 className={cn('min-w-0 flex-1 truncate py-2 text-xl font-semibold leading-tight text-ink-gray-9', backTo && 'sr-only')}>{title}</h1>
          {mobileAction && <div className="flex shrink-0 items-center">{mobileAction}</div>}
        </div>
      </header>

      <header className="hidden pb-6 pt-8 lg:block">
        {breadcrumbs.length > 0 && (
          <nav aria-label={t('common.breadcrumb')} className="mb-2">
            <ol className="flex flex-wrap items-center gap-1 text-base text-ink-gray-6">
              {breadcrumbs.map((crumb, index) => (
                <li key={index} className="flex items-center gap-1">
                  {index > 0 && <ChevronRight size={16} strokeWidth={1.5} aria-hidden="true" />}
                  {crumb.to ? (
                    <Link to={crumb.to} className="rounded underline underline-offset-2 hover:text-ink-gray-9">
                      {crumb.label}
                    </Link>
                  ) : (
                    <span aria-current="page">{crumb.label}</span>
                  )}
                </li>
              ))}
            </ol>
          </nav>
        )}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-3xl font-semibold text-ink-gray-9">{title}</h1>
          {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
        </div>
      </header>

      {/* On a phone the title sits under the back button, in large type. */}
      {backTo && <p aria-hidden="true" className="pt-4 text-2xl font-semibold text-ink-gray-9 lg:hidden">{title}</p>}
      <div className="pt-4 lg:pt-0">{children}</div>
    </>
  );
}

/** Mise en page de détail : contenu principal à gauche, synthèse et actions à droite sur le web. */
export function DetailLayout({ main, aside }: { main: ReactNode; aside: ReactNode }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start lg:gap-6">
      <div className="order-2 min-w-0 space-y-4 lg:order-1 lg:space-y-6">{main}</div>
      <aside className="order-1 min-w-0 space-y-4 lg:sticky lg:top-6 lg:order-2">{aside}</aside>
    </div>
  );
}
