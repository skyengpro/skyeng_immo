import { useTranslation } from 'react-i18next';
import { DetailList } from '@/components/DetailList';
import { DetailLayout } from '@/components/Page';
import { StatusBadge } from '@/components/StatusBadge';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import type { IssueDetail } from '@/data/types';
import { useFormat } from '@/lib/format';

/** A request: where it stands, what was reported, what the manager answered. */
export function IssueDetailView({ issue }: { issue: IssueDetail }) {
  const { t } = useTranslation();
  const format = useFormat();

  return (
    <DetailLayout
      aside={
        <Card>
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <StatusBadge kind="issue" value={issue.status} />
              {issue.urgent && <Badge tone="red">{t('issue.urgent')}</Badge>}
            </div>
            <p className="text-ink-gray-8">{t(`issue.statusHelp.${issue.status}`)}</p>
            <DetailList
              items={[
                { label: t('issue.number'), value: <span className="tabular">{issue.id}</span> },
                { label: t('issue.category'), value: t(`issueCategory.${issue.category}`) },
                ...(issue.property ? [{ label: t('issue.property'), value: issue.property.displayName }] : []),
                { label: t('issue.createdAt'), value: format.date(issue.createdAt) },
              ]}
            />
          </div>
        </Card>
      }
      main={
        <>
          <Card title={t('issue.description')}>
            <div className="space-y-4">
              <p className="whitespace-pre-line text-ink-gray-8">{issue.description}</p>
              {issue.photo && (
                <img src={issue.photo} alt={t('issue.photoAlt', { title: issue.title })} className="max-h-96 w-full rounded-xl border border-outline-gray-2 object-contain" />
              )}
            </div>
          </Card>

          {issue.resolution && (
            <Card title={t('issue.resolution')}>
              <p className="whitespace-pre-line text-ink-gray-8">{issue.resolution}</p>
            </Card>
          )}

          <Card title={t('issue.replies')}>
            {issue.replies.length === 0 ? (
              <p className="text-ink-gray-6">{t('issue.noReplies')}</p>
            ) : (
              <ul className="space-y-3">
                {issue.replies.map((reply, index) => (
                  <li key={index} className="rounded border border-outline-gray-2 bg-surface-sidebar p-3">
                    <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
                      <span className="font-semibold text-ink-gray-9">{reply.author}</span>
                      <span className="text-ink-gray-6">{format.dateTime(reply.at)}</span>
                    </div>
                    <p className="whitespace-pre-line text-ink-gray-8">{reply.message}</p>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      }
    />
  );
}
