import { useState } from 'react';
import { Building2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { EmptyState } from '@/components/EmptyState';
import { ListCard } from '@/components/ListCard';
import { Page } from '@/components/Page';
import { PropertyRow } from '@/components/PropertyRow';
import { QueryView } from '@/components/QueryView';
import { Button } from '@/components/ui/Button';
import { FilterChips } from '@/components/ui/Segmented';
import { ListSkeleton } from '@/components/ui/Skeleton';
import * as api from '@/data/api';
import type { PropertyGroup, PropertyList, PropertyStatus } from '@/data/types';
import { cn } from '@/lib/cn';
import { useApi } from '@/lib/useApi';

type Filter = 'all' | PropertyStatus;
const FILTERS: Filter[] = ['all', 'let', 'available', 'ending_soon', 'renovation'];

function Groups({ groups, filter }: { groups: PropertyGroup[]; filter: Filter }) {
  const { t } = useTranslation();
  const visible = groups
    .map((group) => ({ ...group, units: group.units.filter((unit) => filter === 'all' || unit.status === filter) }))
    .filter((group) => group.units.length > 0);
  return (
    <>
      {visible.map((group) => (
        <section key={group.building?.id ?? 'standalone'} className="space-y-2">
          <h3 className="text-lg font-semibold text-ink-gray-8">{group.building?.name ?? t('owner.properties.standalone')}</h3>
          <ListCard>
            {group.units.map((unit) => (
              <PropertyRow key={unit.id} property={unit} />
            ))}
          </ListCard>
        </section>
      ))}
    </>
  );
}

function PropertiesContent({ list }: { list: PropertyList }) {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<Filter>('all');
  const units = list.sections.flatMap((section) => section.groups.flatMap((group) => group.units));

  if (units.length === 0) return <EmptyState icon={Building2} message={t('owner.properties.empty')} />;

  const counts = (value: Filter) => (value === 'all' ? units.length : units.filter((unit) => unit.status === value).length);
  const shown = units.filter((unit) => filter === 'all' || unit.status === filter).length;

  return (
    <div className="space-y-6">
      {units.length > 3 && (
        <FilterChips
          label={t('common.filterBy')}
          value={filter}
          onChange={setFilter}
          options={FILTERS.filter((value) => value === 'all' || counts(value) > 0).map((value) => ({
            value,
            label: `${value === 'all' ? t('common.all') : t(`status.property.${value}`)} (${counts(value)})`,
          }))}
        />
      )}

      {shown === 0 ? (
        <EmptyState
          icon={Building2}
          message={t('owner.properties.filterEmpty')}
          action={
            <Button variant="subtle" onClick={() => setFilter('all')}>
              {t('common.clearFilters')}
            </Button>
          }
        />
      ) : (
        list.sections.map((section) => {
          const sectionCount = section.groups
            .flatMap((group) => group.units)
            .filter((unit) => filter === 'all' || unit.status === filter).length;
          if (sectionCount === 0) return null;
          return (
            <div key={section.landlord?.id ?? 'all'} className={cn('space-y-4', list.byLandlord && 'rounded-xl bg-surface-sidebar p-3 lg:p-4')}>
              {list.byLandlord && (
                <h2 className="text-xl font-semibold">
                  {section.landlord ? t('owner.properties.landlord', { name: section.landlord.name }) : t('owner.properties.noLandlord')}
                </h2>
              )}
              <Groups groups={section.groups} filter={filter} />
            </div>
          );
        })
      )}
    </div>
  );
}

export function PropertiesPage() {
  const { t } = useTranslation();
  const properties = useApi(() => api.listProperties(), []);
  return (
    <Page title={t('nav.properties')} breadcrumbs={[{ label: t('nav.home'), to: '/proprietaire' }, { label: t('nav.properties') }]}>
      <QueryView query={properties} skeleton={<ListSkeleton rows={6} />}>
        {(list) => <PropertiesContent list={list} />}
      </QueryView>
    </Page>
  );
}
