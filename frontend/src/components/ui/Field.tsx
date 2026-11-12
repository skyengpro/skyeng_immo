import { useId, type InputHTMLAttributes, type ReactNode, type TextareaHTMLAttributes } from 'react';
import { cn } from '@/lib/cn';

// Fields: 18 px text (no automatic zoom on iOS), visible border, 48 px high.
const CONTROL =
  'w-full rounded border border-outline-gray-3 bg-surface-base px-3 text-lg text-ink-gray-9 transition-colors hover:border-ink-gray-5 focus:border-ink-gray-8';

interface FieldShellProps {
  id: string;
  label: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  optional?: ReactNode;
  children: ReactNode;
  className?: string;
}

function FieldShell({ id, label, hint, error, optional, children, className }: FieldShellProps) {
  return (
    <div className={cn('space-y-1.5', className)}>
      <label htmlFor={id} className="flex flex-wrap items-baseline gap-x-1 text-body font-semibold text-ink-gray-9 lg:text-base">
        {label}
        {optional && <span className="font-normal text-ink-gray-6">({optional})</span>}
      </label>
      {children}
      {hint && !error && (
        <p id={`${id}-hint`} className="text-base text-ink-gray-6">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="text-base font-semibold text-red-ink">
          {error}
        </p>
      )}
    </div>
  );
}

function describedBy(id: string, hint?: ReactNode, error?: ReactNode) {
  return error ? `${id}-error` : hint ? `${id}-hint` : undefined;
}

interface TextFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'prefix'> {
  label: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  optional?: ReactNode;
  /** Préfixe fixe affiché dans le champ (ex. +237). */
  prefix?: string;
}

export function TextField({ label, hint, error, optional, prefix, className, ...rest }: TextFieldProps) {
  const id = useId();
  const input = (
    <input
      id={id}
      aria-invalid={error ? true : undefined}
      aria-describedby={describedBy(id, hint, error)}
      className={cn(CONTROL, 'min-h-12', prefix && 'rounded-l-none', error && 'border-red-ink hover:border-red-ink focus:border-red-ink')}
      {...rest}
    />
  );
  return (
    <FieldShell id={id} label={label} hint={hint} error={error} optional={optional} className={className}>
      {prefix ? (
        <div className="flex">
          <span className="inline-flex items-center rounded-l border border-r-0 border-outline-gray-2 bg-surface-gray-2 px-3 text-lg text-ink-gray-6 tabular">
            {prefix}
          </span>
          {input}
        </div>
      ) : (
        input
      )}
    </FieldShell>
  );
}

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: ReactNode;
  hint?: ReactNode;
  error?: ReactNode;
  optional?: ReactNode;
}

export function TextArea({ label, hint, error, optional, className, ...rest }: TextAreaProps) {
  const id = useId();
  return (
    <FieldShell id={id} label={label} hint={hint} error={error} optional={optional} className={className}>
      <textarea
        id={id}
        rows={4}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(id, hint, error)}
        className={cn(CONTROL, 'min-h-28 py-2', error && 'border-red-ink hover:border-red-ink focus:border-red-ink')}
        {...rest}
      />
    </FieldShell>
  );
}
