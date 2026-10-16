let authToken = sessionStorage.getItem("ledgermind.sessionToken") || "";
export function setAuthToken(token: string) { authToken = token; if (token) sessionStorage.setItem("ledgermind.sessionToken", token); else sessionStorage.removeItem("ledgermind.sessionToken"); }

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export type BusinessType = "restaurant" | "supermarket" | "trucking" | "contractor" | "hotel" | "farm" | "rental_property" | "school" | "salon" | "training" | "pharmacy";
export interface Business {
  id: string;
  name: string;
  business_type: BusinessType;
  country: string;
  currency: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}
export interface TemplateField {
  name?: string;
  key?: string;
  label?: string;
  type?: string;
  required?: boolean;
  options?: string[];
  [key: string]: unknown;
}
export interface RecordTemplate {
  id: string;
  business_id: string;
  key: string;
  name: string;
  description: string;
  fields: TemplateField[];
}
export interface RecordEntry {
  id: string;
  business_id: string;
  template_id: string;
  values: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
export interface Report {
  business_id: string;
  business_name: string;
  business_type: BusinessType;
  country: string;
  currency: string;
  period: string;
  start_date: string;
  end_date: string;
  timezone: string;
  totals: Record<string, number>;
  counts: Record<string, number>;
  sales_by_payment_method: Record<string, number>;
  expenses_by_category: Record<string, number>;
  daily_breakdown: Array<{date: string; sales_revenue: number; operating_expenses: number; record_count: number}>;
  comparison_to_previous_period: {start_date: string; end_date: string; sales_revenue: number; operating_expenses: number; sales_revenue_change_percent: number | null};
  reconciliation: {sales_minus_incoming_payments: number; status: string; interpretation: string; warning: string};
  data_quality: {records_in_period: number; dated_records_examined: number; undated_or_invalid_date_records_skipped: number; included_record_ids: string[]};
  accounting_note: string;
  supplier_invoice_summary?: {invoice_count: number; invoice_total: number; amount_paid: number; outstanding_balance: number};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}), ...(init?.headers || {}) },
    });
  } catch {
    throw new Error(`Cannot reach LedgerMind API at ${API_BASE}. Start the backend and check the API URL.`);
  }
  if (!response.ok) {
    if (response.status === 401 && authToken && typeof window !== "undefined") {
      window.dispatchEvent(new Event("ledgermind:unauthorized"));
    }
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body);
    } catch { /* keep status message */ }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export interface UserProfile { id: string; full_name: string; email: string; created_at: string; }
export interface AuthSession { access_token: string; token_type: string; expires_at: string; user: UserProfile; }

export const api = {
  register: (payload: {full_name: string; email: string; password: string}) => request<AuthSession>("/auth/register", {method: "POST", body: JSON.stringify(payload)}),
  login: (payload: {email: string; password: string}) => request<AuthSession>("/auth/login", {method: "POST", body: JSON.stringify(payload)}),
  me: () => request<UserProfile>("/auth/me"),
  updateProfile: (full_name: string) => request<UserProfile>("/auth/me", {method: "PATCH", body: JSON.stringify({full_name})}),
  changePassword: (current_password: string, new_password: string) => request<void>("/auth/change-password", {method: "POST", body: JSON.stringify({current_password, new_password})}),
  logout: () => request<void>("/auth/logout", {method: "POST"}),
  businesses: () => request<Business[]>("/businesses"),
  interpretNote: (note: string, businessId?: string) => request<AIInterpretation>("/ai/interpret-record", { method: "POST", body: JSON.stringify({ note, business_id: businessId || null }) }),
  live: () => request<{status: string; service: string}>("/health/live"),
  businessTypes: () => request<Array<{key: BusinessType; label: string; description: string}>>("/business-types"),
  createBusiness: (payload: {name: string; business_type: BusinessType; country: string; currency: string; timezone: string; farm_modules?: Array<"crops" | "livestock" | "poultry">}) =>
    request<Business>("/businesses", {method: "POST", body: JSON.stringify(payload)}),
  business: (id: string) => request<Business>(`/businesses/${id}`),
  templates: (id: string) => request<RecordTemplate[]>(`/businesses/${id}/templates`),
  records: (id: string, templateId?: string) =>
    request<RecordEntry[]>(`/businesses/${id}/records${templateId ? `?template_id=${encodeURIComponent(templateId)}` : ""}`),
  createRecord: (businessId: string, templateId: string, values: Record<string, unknown>) =>
    request<RecordEntry>(`/businesses/${businessId}/templates/${templateId}/records`, {method: "POST", body: JSON.stringify({values})}),
  report: (id: string, period: string) =>
    request<Report>(`/businesses/${id}/reports/summary?period=${encodeURIComponent(period)}`),
  intelligenceIssues: (id: string) => request<IntelligenceResponse>(`/businesses/${id}/intelligence/issues`),
  supplierInvoices: (id: string) => request<SupplierInvoice[]>(`/businesses/${id}/supplier-invoices`),
  createSupplierInvoice: (id: string, payload: {
    supplier: string; invoice_amount: number; amount_paid: number; transaction_date: string;
    reference?: string | null; direction: string; note?: string | null; source_note?: string | null;
  }) => request<SupplierInvoice>(`/businesses/${id}/supplier-invoices`, {method: "POST", body: JSON.stringify(payload)}),
  businessAnalysis: (id: string, question: string, selectedPeriod: string | null) => request<BusinessAnalysis>(
    `/ai/businesses/${id}/analysis`, {method: "POST", body: JSON.stringify({question, period: selectedPeriod})}
  ),
};


export interface IntelligenceIssue {
  type: string;
  severity: string;
  title: string;
  message: string;
  record_ids: string[];
  evidence: Record<string, unknown>;
}
export interface IntelligenceResponse {
  business_id: string;
  business_name: string;
  issues: IntelligenceIssue[];
  summary: { total: number; needs_review: number; informational: number };
  notice: string;
}

export interface AIInterpretation { model: string; saved: boolean; review_required: boolean; extraction: Record<string, unknown>; notice: string; }
export interface SupplierInvoice {
  id: string; business_id: string; created_by_user_id: string; supplier: string;
  invoice_amount: number | string; amount_paid: number | string; outstanding_amount: number | string;
  currency: string; transaction_date: string; reference: string | null; direction: string;
  note: string | null; source_note: string | null; created_at: string;
}
export interface BusinessAnalysis {
  business_id: string; question: string; period: string; start_date: string; end_date: string;
  answer: string; calculated_data: Record<string, unknown>; notice: string;
}
