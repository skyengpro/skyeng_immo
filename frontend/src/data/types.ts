// Shapes returned by skyeng_immo/sky_immo/api.py. Each one notes the Frappe / PropMS / ERPNext source.

export type Lang = 'fr' | 'en';

/** App space: staff (System Manager / Property Manager), landlord, tenant. */
export type Role = 'manager' | 'owner' | 'tenant';

/** Date only, ISO (YYYY-MM-DD). */
export type ISODate = string;
/** Date and time, ISO 8601. */
export type ISODateTime = string;

/** Lease.frequency (PropMS). */
export type Frequency = 'monthly' | 'bimonthly' | 'quarterly' | 'semiannual' | 'annual';

/** Computed from a submitted Sales Invoice: outstanding amount and due date. */
export type InvoiceStatus = 'paid' | 'due' | 'overdue' | 'partly_paid';

/** Lease Invoice Schedule line. "upcoming" = no invoice yet. */
export type ScheduleStatus = InvoiceStatus | 'upcoming';

/** Lease.lease_status. */
export type LeaseStatus = 'active' | 'upcoming' | 'notice_given' | 'expired';

/** Property: computed from its current lease, "renovation" from Property.status. */
export type PropertyStatus = 'let' | 'available' | 'ending_soon' | 'renovation';

/** Issue.status (ERPNext). */
export type IssueStatus = 'open' | 'in_progress' | 'on_hold' | 'resolved' | 'closed';

/** Issue.issue_type, one Issue Type per category. */
export type IssueCategory = 'plumbing' | 'electricity' | 'locksmith' | 'painting' | 'air_conditioning' | 'other';

/** Lease.security_status. */
export type DepositStatus = 'received' | 'partly_received' | 'returned' | 'requested' | 'unknown';

export interface SessionUser {
  id: string;
  role: Role;
  firstName: string;
  fullName: string;
  email: string;
  /** User.language, when set to French or English. */
  language: Lang | null;
}

export interface Session {
  user: SessionUser | null;
  /** Signed in, but the account is not a landlord, tenant or staff member. */
  noAccess: boolean;
  currency: string;
  csrfToken: string | null;
}

/** Property (PropMS): tree of buildings and units. */
export interface PropertyRef {
  id: string;
  name: string;
  /** "Building · Unit" when the unit has a parent. */
  displayName: string;
}

export interface PropertySummary extends PropertyRef {
  /** Property.type (Unit Type), free text entered in the desk. */
  type: string | null;
  status: PropertyStatus;
  tenantName: string | null;
  rent: { amount: number; frequency: Frequency };
}

export interface PropertyGroup {
  /** Parent Property, or null for units without a building. */
  building: { id: string; name: string } | null;
  units: PropertySummary[];
}

export interface PropertySection {
  /** unit_owner Customer; only set when staff see several landlords. */
  landlord: { id: string; name: string } | null;
  groups: PropertyGroup[];
}

export interface PropertyList {
  byLandlord: boolean;
  sections: PropertySection[];
}

export interface Deposit {
  amount: number;
  status: DepositStatus;
}

/** Lease (PropMS), summary. */
export interface LeaseSummary {
  id: string;
  status: LeaseStatus;
  tenant: { id: string; name: string };
  property: PropertyRef;
  startDate: ISODate;
  endDate: ISODate | null;
  frequency: Frequency;
  amountPerPeriod: number;
}

/** Lease Invoice Schedule line, or a period projected until the lease ends. */
export interface ScheduleLine {
  id: string;
  periodStart: ISODate;
  periodEnd: ISODate;
  dueDate: ISODate;
  amount: number;
  outstanding: number;
  status: ScheduleStatus;
  invoiceId: string | null;
}

/** Sales Invoice (ERPNext), summary. */
export interface InvoiceSummary {
  id: string;
  status: InvoiceStatus;
  tenant: { id: string; name: string };
  property: PropertyRef | null;
  leaseId: string | null;
  postingDate: ISODate;
  dueDate: ISODate;
  periodStart: ISODate;
  periodEnd: ISODate;
  total: number;
  outstanding: number;
  daysLate: number;
}

/** Payment Entry (ERPNext), amount allocated to one invoice. */
export interface Payment {
  id: string;
  invoiceId: string;
  date: ISODate;
  amount: number;
  mode: string | null;
  reference: string | null;
  payerName: string | null;
}

export interface InvoiceDetail extends InvoiceSummary {
  items: { label: string; amount: number }[];
  payments: Payment[];
}

export interface LeaseDetail extends LeaseSummary {
  tenantEmail?: string | null;
  tenantPhone?: string | null;
  noticeDays: number;
  deposit: Deposit | null;
  /** Lease Item lines, amount per period. */
  lines: { label: string; amount: number }[];
  schedule: ScheduleLine[];
  invoicesDue: InvoiceSummary[];
  payments: Payment[];
}

export interface OwnerDashboard {
  firstName: string;
  stats: {
    properties: number;
    tenants: number;
    collectedThisMonth: number;
    unpaidTotal: number;
    unpaidCount: number;
  };
  overdue: InvoiceSummary[];
}

export interface PropertyDetail extends PropertySummary {
  buildingName: string | null;
  isBuilding: boolean;
  features: { type: string | null; bedrooms: number; bathrooms: number; area: number; furnished: boolean };
  currentLease: (LeaseSummary & { deposit: Deposit | null; schedule: ScheduleLine[] }) | null;
  invoices: InvoiceSummary[];
  pastLeases: LeaseSummary[];
}

/** Issue (ERPNext). */
export interface IssueSummary {
  id: string;
  title: string;
  category: IssueCategory;
  urgent: boolean;
  status: IssueStatus;
  createdAt: ISODateTime;
  property: PropertyRef | null;
  tenantName: string | null;
}

export interface IssueDetail extends IssueSummary {
  description: string;
  resolution: string | null;
  /** Data URL of the attached photo. */
  photo: string | null;
  replies: { author: string; message: string; at: ISODateTime }[];
}

export interface NewIssueInput {
  category: IssueCategory;
  title: string;
  description: string;
  urgent: boolean;
  property: string | null;
  photo: string | null;
}

export interface TenantHome {
  firstName: string;
  next: { kind: 'invoice'; invoice: InvoiceSummary } | { kind: 'schedule'; line: ScheduleLine } | null;
  balanceDue: number;
  unpaidCount: number;
  homes: { leaseId: string; property: PropertyRef; endDate: ISODate | null }[];
  latestIssue: IssueSummary | null;
}
