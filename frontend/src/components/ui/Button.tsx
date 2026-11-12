import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Link, type LinkProps } from 'react-router';
import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Icon } from './Icon';
import { Spinner } from './Spinner';

export type ButtonVariant = 'solid' | 'subtle' | 'outline' | 'ghost';
export type ButtonSize = 'md' | 'sm';

interface StyleOptions {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
}

const VARIANTS: Record<ButtonVariant, string> = {
  solid: 'bg-primary text-primary-text hover:bg-primary-hover active:bg-primary-active',
  subtle: 'border border-outline-gray-2 bg-surface-gray-2 text-ink-gray-9 hover:bg-surface-gray-3 active:bg-outline-gray-2',
  outline: 'border border-outline-gray-3 bg-surface-base text-ink-gray-8 hover:border-outline-gray-3 active:bg-surface-gray-2',
  ghost: 'bg-transparent text-ink-gray-8 hover:bg-surface-gray-2 active:bg-surface-gray-3',
};

// Large targets everywhere, web included: 48 px high, easy to hit for everyone.
const SIZES: Record<ButtonSize, string> = {
  md: 'min-h-12 px-5 text-body lg:text-base',
  sm: 'min-h-11 px-4 text-base',
};

export function buttonClasses({ variant = 'solid', size = 'md', fullWidth }: StyleOptions = {}) {
  return cn(
    'inline-flex items-center justify-center gap-2 rounded py-2 text-center font-semibold transition-colors',
    'disabled:cursor-not-allowed disabled:bg-surface-gray-2 disabled:text-ink-gray-5 aria-disabled:cursor-not-allowed',
    VARIANTS[variant],
    SIZES[size],
    fullWidth && 'w-full',
  );
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, StyleOptions {
  icon?: LucideIcon;
  loading?: boolean;
  children?: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant, size, fullWidth, icon, loading, className, children, disabled, type = 'button', ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(buttonClasses({ variant, size, fullWidth }), className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading ? <Spinner /> : icon ? <Icon icon={icon} /> : null}
      {children}
    </button>
  );
});

interface ButtonLinkProps extends LinkProps, StyleOptions {
  icon?: LucideIcon;
}

export function ButtonLink({ variant, size, fullWidth, icon, className, children, ...rest }: ButtonLinkProps) {
  return (
    <Link className={cn(buttonClasses({ variant, size, fullWidth }), className)} {...rest}>
      {icon && <Icon icon={icon} />}
      {children}
    </Link>
  );
}
