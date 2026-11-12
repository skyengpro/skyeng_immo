import { useParams } from 'react-router';
import { useTranslation } from 'react-i18next';
import { Page } from '@/components/Page';
import { QueryView } from '@/components/QueryView';
import { DetailSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import { useApi } from '@/lib/useApi';
import { IssueDetailView } from '@/features/shared/IssueDetailView';

export function TenantIssuePage() {
  const { id = '' } = useParams();
  const { t } = useTranslation();
  const issue = useApi(() => api.getIssue(id), [id]);
  const title = issue.data?.title ?? t('nav.maintenance');

  return (
    <Page title={title} backTo="/locataire/maintenance" breadcrumbs={[{ label: t('nav.maintenance'), to: '/locataire/maintenance' }, { label: title }]}>
      <QueryView query={issue} skeleton={<DetailSkeleton />}>
        {(data) => <IssueDetailView issue={data} />}
      </QueryView>
    </Page>
  );
}
