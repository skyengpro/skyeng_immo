/** Concatène des classes CSS en ignorant les valeurs vides ou fausses. */
export function cn(...classes: unknown[]): string {
  return classes.filter((item): item is string => typeof item === 'string' && item.length > 0).join(' ');
}
