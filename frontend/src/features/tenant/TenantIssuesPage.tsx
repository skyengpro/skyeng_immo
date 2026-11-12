import { Plus, Wrench } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/EmptyState';
import { IssueRow } from '@/components/IssueRow';
import { ListCard } from '@/components/ListCard';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { ButtonLink } from '@/components/ui/Button';
import { ListSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import { useApi } from '@/lib/useApi';

const NEW_ISSUE = '/locataire/maintenance/nouvelle';

export function TenantIssuesPage() {
  const { t } = useTranslation();
  const issues = useApi(() => api.listIssues(), []);

  return (
    <Page title={t('nav.maintenance')} breadcrumbs={[{ label: t('nav.home'), to: '/locataire' }, { label: t('nav.maintenance') }]}>
      <div className="space-y-5">
        {/* The main action comes first, big, on every screen size. */}
        <ButtonLink to={NEW_ISSUE} icon={Plus} fullWidth className="lg:w-auto">
          {t('actions.reportIssue')}
        </ButtonLink>
        <QueryView query={issues} skeleton={<ListSkeleton rows={3} />}>
          {(rows) =>
            rows.length === 0 ? (
              <EmptyState icon={Wrench} message={t('tenant.issues.empty')} />
            ) : (
              <section className="space-y-3">
                <h2 className="text-xl font-semibold">{t('tenant.issues.list')}</h2>
                <ListCard>
                  {rows.map((issue) => (
                    <IssueRow key={issue.id} issue={issue} to={`/locataire/maintenance/${encodeURIComponent(issue.id)}`} />
                  ))}
                </ListCard>
              </section>
            )
          }
        </QueryView>
      </div>
    </Page>
  );
}
