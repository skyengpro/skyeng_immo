import { useTranslation } from 'react-i18next';
import type { PropertySummary } from '@/data/types';
import { useFormat } from '@/lib/format';
import { StatusBadge } from './StatusBadge';
import { ListRow } from './ListCard';

/** Unit card: name, status, current tenant or "Vacant", rent. */
export function PropertyRow({ property }: { property: PropertySummary }) {
  const { t } = useTranslation();
  const format = useFormat();
  return (
    <ListRow to={`/proprietaire/biens/${encodeURIComponent(property.id)}`}>
      <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-1">
        <div className="min-w-0">
          <p className="text-lg font-semibold text-ink-gray-9">{property.name}</p>
          {property.type && <p className="text-ink-gray-6">{property.type}</p>}
        </div>
        <StatusBadge kind="property" value={property.status} />
      </div>
      <div className="mt-2 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
        <span className={property.tenantName ? 'font-medium text-ink-gray-9' : 'text-ink-gray-6'}>
          {property.tenantName ?? t('common.vacant')}
        </span>
        {property.rent.amount > 0 && (
          <span className="font-semibold text-ink-gray-9 tabular">
            {t(`per.${property.rent.frequency}`, { amount: format.money(property.rent.amount) })}
          </span>
        )}
      </div>
    </ListRow>
  );
}
