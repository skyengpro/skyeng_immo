// Navigation of each space. `short` is the phone tab bar label; `exact` lights the item only on its own page.
export const ownerNav = [
  { to: '/proprietaire', label: 'Home', short: 'Home', icon: 'lucide-layout-grid', exact: true },
  { to: '/proprietaire/biens', label: 'My properties', short: 'Properties', icon: 'lucide-building-2', also: ['/proprietaire/factures'] },
  // A tenant's page is their lease (/proprietaire/baux/<lease>).
  { to: '/proprietaire/locataires', label: 'Tenants', short: 'Tenants', icon: 'lucide-users-round', also: ['/proprietaire/baux'] },
  { to: '/proprietaire/maintenance', label: 'Repairs', short: 'Repairs', icon: 'lucide-wrench', badge: 'awaiting' },
  { to: '/proprietaire/compte', label: 'My account', short: 'Account', icon: 'lucide-user-round' },
]

export const tenantNav = [
  { to: '/locataire', label: 'Home', short: 'Home', icon: 'lucide-layout-grid', exact: true },
  { to: '/locataire/bail', label: 'My lease', short: 'Lease', icon: 'lucide-file-text' },
  { to: '/locataire/factures', label: 'Invoices', short: 'Invoices', icon: 'lucide-receipt-text' },
  { to: '/locataire/maintenance', label: 'Repairs', short: 'Repairs', icon: 'lucide-wrench' },
  { to: '/locataire/compte', label: 'My account', short: 'Account', icon: 'lucide-user-round' },
]

export function isActive(item, path) {
  if (item.exact) return path === item.to
  return [item.to, ...(item.also || [])].some((p) => path === p || path.startsWith(`${p}/`))
}
