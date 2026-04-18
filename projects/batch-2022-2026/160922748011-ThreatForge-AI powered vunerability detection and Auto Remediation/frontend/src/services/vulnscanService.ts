// services/vulnscanService.ts
// VulnScan API Service Layer — integrates with backend at localhost:8000

const BASE_URL = "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Module {
  name: string;
  description: string;
}

export interface ScanRequest {
  target_url: string;
  scan_type: "full" | "quick" | "targeted";
  consent_confirmed: boolean;
  requester_name: string;
  organization: string;
  notes?: string;
  modules?: string[] | null;
}

export interface ScanQueued {
  scan_id: string;
  status: string;
  target_url: string;
  modules: string[];
  message: string;
}

export interface ScanStatus {
  id: string;
  target_url: string;
  status: "queued" | "running" | "completed" | "failed";
  scan_type: string;
  modules_requested: string[];
  modules_completed: string[];
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  findings: Finding[];
}

export interface ScanSummary {
  id: string;
  target_url: string;
  status: string;
  scan_type: string;
  organization: string;
  created_at: string;
  total_findings: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface Finding {
  id: string;
  module: string;
  title: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
  cvss_score: number;
  cve_id: string | null;
  cwe_id: string | null;
  description: string;
  evidence: string;
  affected_url: string;
  parameter: string | null;
  remediation: string;
  reference_links: string[];
  discovered_at: string;
}

export interface Report {
  scan_id: string;
  target_url: string;
  organization: string;
  scan_type: string;
  risk_score: number;
  severity_summary: Record<string, number>;
  priority_findings: Finding[];
  all_findings: Finding[];
  modules_run: string[];
  gemini_insight: string | null;
}

export interface Analytics {
  total_scans: number;
  completed_scans: number;
  total_findings: number;
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  orgs_scanned: number;
}

// ─── API Helpers ──────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (res.status === 204) return undefined as T;

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data?.error || data?.detail || `HTTP ${res.status}`);
  }

  return data as T;
}

// ─── API Functions ────────────────────────────────────────────────────────────

export const vulnscanAPI = {
  listModules: () =>
    apiFetch<{ modules: Module[] }>("/api/vulnscan/modules").then(
      (r) => r.modules
    ),

  queueScan: (body: ScanRequest) =>
    apiFetch<ScanQueued>("/api/vulnscan/scans", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getScanStatus: (scanId: string) =>
    apiFetch<ScanStatus>(`/api/vulnscan/scans/${scanId}`),

  listScans: (status?: string, limit = 50) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    params.set("limit", String(limit));
    return apiFetch<{ total: number; scans: ScanSummary[] }>(
      `/api/vulnscan/scans?${params}`
    );
  },

  getFindings: (scanId: string, severity?: string, module?: string) => {
    const params = new URLSearchParams();
    if (severity) params.set("severity", severity);
    if (module) params.set("module", module);
    return apiFetch<{ scan_id: string; total: number; findings: Finding[] }>(
      `/api/vulnscan/scans/${scanId}/findings?${params}`
    );
  },

  getReport: (scanId: string) =>
    apiFetch<Report>(`/api/vulnscan/reports/${scanId}`),

  getAnalytics: () => apiFetch<Analytics>("/api/vulnscan/analytics"),

  deleteScan: (scanId: string) =>
    apiFetch<void>(`/api/vulnscan/scans/${scanId}`, { method: "DELETE" }),
};