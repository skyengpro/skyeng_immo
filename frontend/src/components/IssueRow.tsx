import { useTranslation } from 'react-i18next';
import type { IssueSummary } from '@/data/types';
import { useFormat } from '@/lib/format';
import { StatusBadge } from './StatusBadge';
import { ListRow } from './ListCard';

/** Maintenance request row. */
export function IssueRow({ issue, to }: { issue: IssueSummary; to: string }) {
  const { t } = useTranslation();
  const format = useFormat();
  return (
    <ListRow to={to}>
      <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
        <p className="min-w-0 font-semibold text-ink-gray-9">{issue.title}</p>
        <StatusBadge kind="issue" value={issue.status} />
      </div>
      <p className="mt-1 text-ink-gray-6">
        {t('issue.row', { date: format.date(issue.createdAt), category: t(`issueCategory.${issue.category}`) })}
      </p>
    </ListRow>
  );
}
