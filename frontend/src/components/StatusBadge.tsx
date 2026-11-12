import { useTranslation } from 'react-i18next';
import type { DepositStatus, InvoiceStatus, IssueStatus, LeaseStatus, PropertyStatus, ScheduleStatus } from '@/data/types';
import { Badge, type BadgeTone } from './ui/Badge';

const TONES = {
  invoice: { paid: 'green', due: 'orange', overdue: 'red', partly_paid: 'yellow' },
  schedule: { paid: 'green', due: 'orange', overdue: 'red', partly_paid: 'yellow', upcoming: 'blue' },
  lease: { active: 'green', upcoming: 'blue', notice_given: 'orange', expired: 'gray' },
  property: { let: 'green', available: 'gray', ending_soon: 'orange', renovation: 'yellow' },
  issue: { open: 'blue', in_progress: 'yellow', on_hold: 'yellow', resolved: 'green', closed: 'gray' },
  deposit: { received: 'green', partly_received: 'yellow', returned: 'gray', requested: 'orange', unknown: 'gray' },
} satisfies Record<string, Record<string, BadgeTone>>;

type StatusProps =
  | { kind: 'invoice'; value: InvoiceStatus }
  | { kind: 'schedule'; value: ScheduleStatus }
  | { kind: 'lease'; value: LeaseStatus }
  | { kind: 'property'; value: PropertyStatus }
  | { kind: 'issue'; value: IssueStatus }
  | { kind: 'deposit'; value: DepositStatus };

export function StatusBadge(props: StatusProps) {
  const { t } = useTranslation();
  const tones: Record<string, BadgeTone> = TONES[props.kind];
  return <Badge tone={tones[props.value] ?? 'gray'}>{t(`status.${props.kind}.${props.value}` as 'status.invoice.paid')}</Badge>;
}
