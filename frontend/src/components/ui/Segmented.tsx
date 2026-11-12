import { useRef, type KeyboardEvent, type ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface Option<T extends string> {
  value: T;
  label: ReactNode;
  /** Libellé accessible si le libellé visible est abrégé. */
  ariaLabel?: string;
  lang?: string;
}

interface SegmentedProps<T extends string> {
  label: string;
  options: Option<T>[];
  value: T;
  onChange: (value: T) => void;
  /** « tabs » pour des onglets, « radio » pour un choix exclusif. */
  mode?: 'tabs' | 'radio';
  /** Identifiant du panneau contrôlé, pour les onglets. */
  panelId?: string;
  className?: string;
  fullWidth?: boolean;
}

/** Contrôle segmenté sur fond gris : onglets ou choix exclusif, navigable aux flèches. */
export function Segmented<T extends string>({ label, options, value, onChange, mode = 'radio', panelId, className, fullWidth }: SegmentedProps<T>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = (index + step + options.length) % options.length;
    refs.current[next]?.focus();
    onChange(options[next].value);
  }

  return (
    <div
      role={mode === 'tabs' ? 'tablist' : 'radiogroup'}
      aria-label={label}
      className={cn('inline-flex max-w-full gap-0.5 rounded bg-surface-gray-2 p-0.5', fullWidth && 'flex w-full', className)}
    >
      {options.map((option, index) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            ref={(element) => {
              refs.current[index] = element;
            }}
            type="button"
            role={mode === 'tabs' ? 'tab' : 'radio'}
            aria-selected={mode === 'tabs' ? selected : undefined}
            aria-checked={mode === 'radio' ? selected : undefined}
            aria-controls={mode === 'tabs' ? panelId : undefined}
            aria-label={option.ariaLabel}
            lang={option.lang}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(option.value)}
            onKeyDown={(event) => onKeyDown(event, index)}
            className={cn(
              'inline-flex min-h-11 items-center justify-center gap-1.5 rounded px-4 text-body font-semibold transition-colors lg:text-base',
              fullWidth && 'flex-1',
              selected ? 'bg-surface-base text-ink-gray-9 shadow-float ring-1 ring-outline-gray-3' : 'text-ink-gray-6 hover:text-ink-gray-9',
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

interface ChipsProps<T extends string> {
  label: string;
  options: { value: T; label: ReactNode }[];
  value: T;
  onChange: (value: T) => void;
}

/** Filtres en pastilles, qui passent à la ligne si la place manque. */
export function FilterChips<T extends string>({ label, options, value, onChange }: ChipsProps<T>) {
  return (
    <div role="group" aria-label={label} className="flex flex-wrap gap-2">
      {options.map((option) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
            className={cn(
              'inline-flex min-h-11 items-center gap-1.5 rounded-full border px-4 text-body font-semibold transition-colors lg:text-base',
              selected
                ? 'border-primary bg-primary text-primary-text'
                : 'border-outline-gray-3 bg-surface-base text-ink-gray-8 hover:border-ink-gray-5',
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
