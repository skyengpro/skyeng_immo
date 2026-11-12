import { LoaderCircle } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Icon } from './Icon';

export function Spinner({ className }: { className?: string }) {
  return <Icon icon={LoaderCircle} className={cn('animate-spin motion-reduce:animate-none', className)} />;
}
