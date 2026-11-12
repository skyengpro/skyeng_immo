// Data access layer. Screens only go through this file.
// Every call is a whitelisted method of skyeng_immo/mon_immo/api.py on the Frappe site,
// authenticated by the Frappe session cookie (same origin).
import type {
  InvoiceDetail,
  InvoiceSummary,
  IssueDetail,
  IssueSummary,
  Lang,
  LeaseDetail,
  LeaseSummary,
  NewIssueInput,
  OwnerDashboard,
  PropertyDetail,
  PropertyList,
  Session,
  TenantHome,
} from './types';

export type ApiErrorKind = 'network' | 'not_found' | 'forbidden' | 'invalid_credentials' | 'invalid_input';

export class ApiError extends Error {
  constructor(
    public readonly kind: ApiErrorKind,
    /** Message from the server, already translated by Frappe, when there is one. */
    public readonly serverMessage?: string,
  ) {
    super(kind);
    this.name = 'ApiError';
  }
}

const METHOD = '/api/method/';
const APP = 'skyeng_immo.mon_immo.api.';

let csrfToken: string | null = null;

/* -------------------------------------------------------------------------- */
/* Session-lost notification: a 403 on a signed-in screen means the session   */
/* ended (sign-out elsewhere, expiry). The app state re-reads the session.     */
/* -------------------------------------------------------------------------- */

const authListeners = new Set<() => void>();

export function onAuthError(listener: () => void): () => void {
  authListeners.add(listener);
  return () => authListeners.delete(listener);
}

function serverMessage(body: Record<string, unknown> | null): string | undefined {
  const raw = body?._server_messages;
  if (typeof raw !== 'string') return undefined;
  try {
    const messages = (JSON.parse(raw) as string[]).map((item) => {
      try {
        return (JSON.parse(item) as { message?: string }).message ?? item;
      } catch {
        return item;
      }
    });
    // Frappe messages may contain simple HTML (<b>…</b>).
    const text = messages.join(' ').replace(/<[^>]+>/g, '');
    return text.trim() || undefined;
  } catch {
    return undefined;
  }
}

function errorKind(status: number, excType: unknown): ApiErrorKind {
  if (status === 401 || excType === 'AuthenticationError') return 'invalid_credentials';
  if (status === 404 || excType === 'DoesNotExistError') return 'not_found';
  if (status === 403 || excType === 'PermissionError') return 'forbidden';
  if (status === 417 || status === 400 || excType === 'ValidationError') return 'invalid_input';
  return 'network';
}

async function request<T>(
  httpMethod: 'GET' | 'POST',
  method: string,
  params: Record<string, unknown> = {},
  retried = false,
): Promise<T> {
  let url = `${METHOD}${method}`;
  const headers: Record<string, string> = { Accept: 'application/json' };
  const init: RequestInit = { method: httpMethod, credentials: 'same-origin', headers };

  if (httpMethod === 'GET') {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) query.set(key, String(value));
    }
    const qs = query.toString();
    if (qs) url += `?${qs}`;
  } else {
    headers['Content-Type'] = 'application/json';
    if (csrfToken) headers['X-Frappe-CSRF-Token'] = csrfToken;
    init.body = JSON.stringify(params);
  }

  let response: Response;
  try {
    response = await fetch(url, init);
  } catch {
    throw new ApiError('network');
  }

  let body: Record<string, unknown> | null = null;
  try {
    body = (await response.json()) as Record<string, unknown>;
  } catch {
    body = null;
  }

  if (response.ok) return body?.message as T;

  // The CSRF token changes when the session does: read it again once, then retry.
  if (!retried && body?.exc_type === 'CSRFTokenError') {
    await getSession();
    return request<T>(httpMethod, method, params, true);
  }

  const kind = errorKind(response.status, body?.exc_type);
  if (kind === 'forbidden') authListeners.forEach((listener) => listener());
  throw new ApiError(kind, serverMessage(body));
}

const get = <T>(name: string, params?: Record<string, unknown>) => request<T>('GET', APP + name, params);
const post = <T>(name: string, params?: Record<string, unknown>) => request<T>('POST', APP + name, params);

/* -------------------------------------------------------------------------- */
/* Session                                                                    */
/* -------------------------------------------------------------------------- */

export async function getSession(): Promise<Session> {
  const session = await get<Session>('get_session');
  csrfToken = session.csrfToken;
  return session;
}

/** Frappe's own sign-in. A wrong password answers 401. */
export async function login(email: string, password: string): Promise<Session> {
  await request('POST', 'login', { usr: email.trim(), pwd: password });
  return getSession();
}

export async function logout(): Promise<void> {
  try {
    await request('POST', 'logout');
  } finally {
    csrfToken = null;
  }
}

/** Sends Frappe's "reset your password" email. Same answer whether the account exists or not. */
export async function requestPasswordReset(email: string): Promise<void> {
  try {
    await request('POST', 'frappe.core.doctype.user.user.reset_password', { user: email.trim() });
  } catch (error) {
    if (error instanceof ApiError && error.kind === 'network') throw error;
  }
}

export function setLanguage(lang: Lang): Promise<void> {
  return post('set_language', { lang });
}

/* -------------------------------------------------------------------------- */
/* Landlord and property manager                                              */
/* -------------------------------------------------------------------------- */

export const getOwnerDashboard = () => get<OwnerDashboard>('get_owner_dashboard');
export const listProperties = () => get<PropertyList>('list_properties');
export const getProperty = (name: string) => get<PropertyDetail>('get_property', { name });

/* -------------------------------------------------------------------------- */
/* Leases and invoices (both spaces; the server filters by the signed-in user) */
/* -------------------------------------------------------------------------- */

export const getLease = (name: string) => get<LeaseDetail>('get_lease', { name });
export const listInvoices = (tab: 'unpaid' | 'paid') => get<InvoiceSummary[]>('list_invoices', { tab });
export const getInvoice = (name: string) => get<InvoiceDetail>('get_invoice', { name });

/** PDF from the ERPNext print format: the invoice, or the receipt (Payment Entry). */
export function downloadUrl(kind: 'invoice' | 'receipt', name: string): string {
  const query = new URLSearchParams({ kind, name });
  return `${METHOD}${APP}download?${query.toString()}`;
}

/* -------------------------------------------------------------------------- */
/* Tenant                                                                     */
/* -------------------------------------------------------------------------- */

export const getTenantHome = () => get<TenantHome>('get_tenant_home');
export const listMyLeases = () => get<LeaseSummary[]>('list_my_leases');
export const listIssues = () => get<IssueSummary[]>('list_issues');
export const getIssue = (name: string) => get<IssueDetail>('get_issue', { name });

export function createIssue(input: NewIssueInput): Promise<{ id: string }> {
  return post('create_issue', {
    category: input.category,
    title: input.title,
    description: input.description,
    urgent: input.urgent ? 1 : 0,
    property: input.property,
    photo: input.photo,
  });
}
