import type { LucideIcon } from 'lucide-react';

/** lucide-react icons: 22 px, stroke 1.75, always next to a text label. */
export function Icon({ icon: Glyph, className, size = 22 }: { icon: LucideIcon; className?: string; size?: number }) {
  return <Glyph size={size} strokeWidth={1.75} aria-hidden="true" className={className ? `shrink-0 ${className}` : 'shrink-0'} />;
}
