import { Building2, FileText, House, ReceiptText, UserRound, Wrench, type LucideIcon } from 'lucide-react';
import type { Role } from '@/data/types';

/** Where the Frappe site serves the app (hooks.py: website_route_rules). */
export const APP_ROUTE = '/mon-immo';

export interface NavItem {
  to: string;
  label: 'nav.home' | 'nav.properties' | 'nav.account' | 'nav.myLease' | 'nav.invoices' | 'nav.maintenance';
  icon: LucideIcon;
  /** Route prefixes that make the entry active (a property page keeps "My properties" lit). */
  prefixes: string[];
}

const OWNER: NavItem[] = [
  { to: '/proprietaire', label: 'nav.home', icon: House, prefixes: [] },
  { to: '/proprietaire/biens', label: 'nav.properties', icon: Building2, prefixes: ['/proprietaire/biens', '/proprietaire/baux', '/proprietaire/factures'] },
  { to: '/proprietaire/compte', label: 'nav.account', icon: UserRound, prefixes: [] },
];

const TENANT: NavItem[] = [
  { to: '/locataire', label: 'nav.home', icon: House, prefixes: [] },
  { to: '/locataire/bail', label: 'nav.myLease', icon: FileText, prefixes: ['/locataire/bail'] },
  { to: '/locataire/factures', label: 'nav.invoices', icon: ReceiptText, prefixes: ['/locataire/factures'] },
  { to: '/locataire/maintenance', label: 'nav.maintenance', icon: Wrench, prefixes: ['/locataire/maintenance'] },
  { to: '/locataire/compte', label: 'nav.account', icon: UserRound, prefixes: [] },
];

/** Staff use the landlord screens over every property. */
export function spaceOf(role: Role): 'owner' | 'tenant' {
  return role === 'tenant' ? 'tenant' : 'owner';
}

export function navigationFor(role: Role): NavItem[] {
  return spaceOf(role) === 'tenant' ? TENANT : OWNER;
}

export function homePath(role: Role): string {
  return spaceOf(role) === 'tenant' ? '/locataire' : '/proprietaire';
}

export function isNavActive(item: NavItem, pathname: string): boolean {
  if (pathname === item.to) return true;
  return item.prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

/** Which space a route belongs to, if any. */
export function routeSpace(pathname: string): 'owner' | 'tenant' | null {
  if (pathname === '/proprietaire' || pathname.startsWith('/proprietaire/')) return 'owner';
  if (pathname === '/locataire' || pathname.startsWith('/locataire/')) return 'tenant';
  return null;
}
