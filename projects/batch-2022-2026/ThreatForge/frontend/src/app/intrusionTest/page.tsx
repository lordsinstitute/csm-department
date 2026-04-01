"use client";

import Link from "next/link";
import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Loader2,
  ChevronDown,
  Shield,
  Search,
  List,
  BarChart3,
  FileText,
  Trash2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  X,
  Filter,
  Zap,
  Target,
  Info,
  ChevronRight,
  ExternalLink,
  Copy,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

// ─── Inline API Service ───────────────────────────────────────────────────────

const BASE_URL = "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => ({}));
  if (!res.ok)
    throw new Error(data?.error || data?.detail || `HTTP ${res.status}`);
  return data as T;
}

const api = {
  listModules: () =>
    apiFetch<{ modules: { name: string; description: string }[] }>(
      "/api/vulnscan/modules",
    ).then((r) => r.modules),
  queueScan: (body: object) =>
    apiFetch<any>("/api/vulnscan/scans", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getScanStatus: (id: string) =>
    apiFetch<ScanData>(`/api/vulnscan/scans/${id}`),
  listScans: (status?: string, limit = 50) =>
    apiFetch<{ total: number; scans: ScanSummary[] }>(
      `/api/vulnscan/scans?${status ? `status=${status}&` : ""}limit=${limit}`,
    ),
  getFindings: (id: string, severity?: string, module?: string) =>
    apiFetch<{ scan_id: string; total: number; findings: Finding[] }>(
      `/api/vulnscan/scans/${id}/findings?${severity ? `severity=${severity}&` : ""}${module ? `module=${module}` : ""}`,
    ),
  getReport: (id: string) => apiFetch<Report>(`/api/vulnscan/reports/${id}`),
  getAnalytics: () => apiFetch<Analytics>("/api/vulnscan/analytics"),
  deleteScan: (id: string) =>
    apiFetch<void>(`/api/vulnscan/scans/${id}`, { method: "DELETE" }),
};

// ─── Types ────────────────────────────────────────────────────────────────────

interface Finding {
  id: string;
  scan_id?: string;
  module: string;
  title: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
  cvss_score: string | number;
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

interface ScanData {
  id: string;
  target_url: string;
  status: "queued" | "running" | "completed" | "failed";
  scan_type: string;
  requester_name?: string;
  organization?: string;
  notes?: string;
  modules_requested: string[];
  modules_completed: string[];
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  findings: Finding[];
}

interface ScanSummary {
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

interface Report {
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

interface Analytics {
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

// ─── Severity config ──────────────────────────────────────────────────────────

const SEV: Record<
  string,
  { badge: string; bar: string; border: string; bg: string; text: string }
> = {
  CRITICAL: {
    badge: "bg-red-600 text-white",
    bar: "bg-red-500",
    border: "border-red-500/50",
    bg: "bg-red-500/10",
    text: "text-red-400",
  },
  HIGH: {
    badge: "bg-orange-500 text-white",
    bar: "bg-orange-500",
    border: "border-orange-500/50",
    bg: "bg-orange-500/10",
    text: "text-orange-400",
  },
  MEDIUM: {
    badge: "bg-yellow-500 text-black",
    bar: "bg-yellow-500",
    border: "border-yellow-500/50",
    bg: "bg-yellow-500/10",
    text: "text-yellow-400",
  },
  LOW: {
    badge: "bg-blue-500 text-white",
    bar: "bg-blue-500",
    border: "border-blue-500/50",
    bg: "bg-blue-500/10",
    text: "text-blue-400",
  },
  INFO: {
    badge: "bg-gray-500 text-white",
    bar: "bg-gray-500",
    border: "border-gray-500/50",
    bg: "bg-gray-500/10",
    text: "text-gray-400",
  },
};

function SeverityBadge({ sev }: { sev: string }) {
  const c = SEV[sev] ?? SEV.INFO;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${c.badge}`}
    >
      {sev}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; icon: React.ReactNode }> = {
    queued: {
      cls: "bg-gray-500/20 text-gray-300 border border-gray-500/40",
      icon: <Clock className="h-3 w-3" />,
    },
    running: {
      cls: "bg-blue-500/20 text-blue-300 border border-blue-500/40",
      icon: <Loader2 className="h-3 w-3 animate-spin" />,
    },
    completed: {
      cls: "bg-green-500/20 text-green-300 border border-green-500/40",
      icon: <CheckCircle className="h-3 w-3" />,
    },
    failed: {
      cls: "bg-red-500/20 text-red-300 border border-red-500/40",
      icon: <AlertTriangle className="h-3 w-3" />,
    },
  };
  const s = map[status] ?? map.queued;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${s.cls}`}
    >
      {s.icon}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function ErrBox({ msg, onClose }: { msg: string; onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-red-900/30 border border-red-500/50 rounded-lg p-3 flex items-start gap-2.5"
    >
      <AlertTriangle className="h-4 w-4 text-red-400 shrink-0 mt-0.5" />
      <p className="text-red-300 text-sm flex-1">{msg}</p>
      <button onClick={onClose}>
        <X className="h-4 w-4 text-red-400 hover:text-red-200" />
      </button>
    </motion.div>
  );
}

function Spinner({ text = "Loading…" }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-14 gap-3">
      <Loader2 className="h-7 w-7 animate-spin text-blue-400" />
      <p className="text-sm text-muted-foreground">{text}</p>
    </div>
  );
}

// ─── Finding Card ─────────────────────────────────────────────────────────────

function FindingCard({
  f,
  defaultOpen = false,
}: {
  f: Finding;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);
  const c = SEV[f.severity] ?? SEV.INFO;

  const copy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`rounded-xl border ${c.border} overflow-hidden transition-all`}
    >
      {/* Header row */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-white/[0.03] transition-colors"
      >
        <div className={`mt-0.5 p-1.5 rounded-md ${c.bg}`}>
          <Shield className={`h-3.5 w-3.5 ${c.text}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <SeverityBadge sev={f.severity} />
            <span className="text-xs font-mono text-muted-foreground bg-background/60 px-1.5 py-0.5 rounded">
              {f.module}
            </span>
            {f.cvss_score && (
              <span className="text-xs text-muted-foreground">
                CVSS {f.cvss_score}
              </span>
            )}
            {f.cwe_id && (
              <span className="text-xs text-muted-foreground">{f.cwe_id}</span>
            )}
          </div>
          <p className="text-sm font-semibold text-foreground">{f.title}</p>
          <p className="text-xs text-muted-foreground mt-0.5 truncate">
            {f.affected_url}
          </p>
        </div>
        <ChevronRight
          className={`h-4 w-4 text-muted-foreground shrink-0 mt-1 transition-transform ${open ? "rotate-90" : ""}`}
        />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-5 pt-1 space-y-4 border-t border-white/[0.06]">
              {/* Affected URL */}
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5">
                  Affected URL
                </p>
                <div className="flex items-center gap-2 bg-background/60 rounded-lg px-3 py-2 border border-border/30">
                  <code className="text-xs text-blue-300 flex-1 break-all">
                    {f.affected_url}
                  </code>
                  <button
                    onClick={() => copy(f.affected_url)}
                    className="shrink-0 text-muted-foreground hover:text-foreground"
                  >
                    {copied ? (
                      <Check className="h-3.5 w-3.5 text-green-400" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Description */}
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5">
                  Description
                </p>
                <p className="text-sm text-foreground/90 leading-relaxed">
                  {f.description}
                </p>
              </div>

              {/* Evidence */}
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5">
                  Evidence
                </p>
                <div className="bg-black/40 border border-white/[0.08] rounded-lg px-3 py-2.5">
                  <code className="text-xs text-green-300 break-all">
                    {f.evidence}
                  </code>
                </div>
              </div>

              {/* Remediation */}
              <div className={`rounded-lg p-3 border ${c.border} ${c.bg}`}>
                <p
                  className={`text-xs font-semibold uppercase tracking-wide mb-1 ${c.text}`}
                >
                  Remediation
                </p>
                <p className="text-sm text-foreground/90">{f.remediation}</p>
              </div>

              {/* Meta row */}
              <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                {f.cve_id && (
                  <span className="bg-background/60 border border-border/40 rounded px-2 py-0.5">
                    CVE: {f.cve_id}
                  </span>
                )}
                {f.cwe_id && (
                  <span className="bg-background/60 border border-border/40 rounded px-2 py-0.5">
                    {f.cwe_id}
                  </span>
                )}
                {f.parameter && (
                  <span className="bg-background/60 border border-border/40 rounded px-2 py-0.5">
                    param: {f.parameter}
                  </span>
                )}
                <span className="bg-background/60 border border-border/40 rounded px-2 py-0.5">
                  {new Date(f.discovered_at).toLocaleString()}
                </span>
              </div>

              {/* Reference links */}
              {f.reference_links?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1.5">
                    References
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {f.reference_links.map((link, i) => (
                      <a
                        key={i}
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 bg-blue-500/10 border border-blue-500/30 rounded px-2 py-0.5 transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        {new URL(link).hostname}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── Scan Result View ─────────────────────────────────────────────────────────
// This renders the full scan data matching your Postman response exactly

function ScanResultView({ scan }: { scan: ScanData }) {
  const [severityFilter, setSeverityFilter] = useState("");
  const [moduleFilter, setModuleFilter] = useState("");

  const severityCounts = scan.findings.reduce<Record<string, number>>(
    (acc, f) => {
      acc[f.severity] = (acc[f.severity] || 0) + 1;
      return acc;
    },
    {},
  );

  const modules = Array.from(new Set(scan.findings.map((f) => f.module)));

  const filtered = scan.findings.filter((f) => {
    if (severityFilter && f.severity !== severityFilter) return false;
    if (moduleFilter && f.module !== moduleFilter) return false;
    return true;
  });

  const duration =
    scan.started_at && scan.completed_at
      ? (
          (new Date(scan.completed_at).getTime() -
            new Date(scan.started_at).getTime()) /
          1000
        ).toFixed(1)
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5"
    >
      {/* ── Scan Header ── */}
      <div className="p-5 bg-background/50 border border-white/10 rounded-xl space-y-4">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="flex-1 min-w-0">
            <p className="text-base font-semibold text-foreground break-all">
              {scan.target_url}
            </p>
            <p className="text-xs font-mono text-muted-foreground mt-1">
              {scan.id}
            </p>
          </div>
          <StatusBadge status={scan.status} />
        </div>

        {/* Meta grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Scan Type", value: scan.scan_type },
            { label: "Requester", value: scan.requester_name || "—" },
            { label: "Organization", value: scan.organization || "—" },
            { label: "Duration", value: duration ? `${duration}s` : "—" },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="bg-background/40 border border-white/[0.06] rounded-lg px-3 py-2.5"
            >
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-sm font-medium text-foreground mt-0.5 capitalize">
                {value}
              </p>
            </div>
          ))}
        </div>

        {/* Timestamps */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          <span>Created: {new Date(scan.created_at).toLocaleString()}</span>
          {scan.started_at && (
            <span>Started: {new Date(scan.started_at).toLocaleString()}</span>
          )}
          {scan.completed_at && (
            <span>
              Completed: {new Date(scan.completed_at).toLocaleString()}
            </span>
          )}
        </div>

        {/* Modules */}
        <div>
          <p className="text-xs text-muted-foreground mb-2">
            Modules Completed ({scan.modules_completed.length}/
            {scan.modules_requested.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {scan.modules_requested.map((m) => (
              <span
                key={m}
                className={`px-2 py-0.5 rounded text-xs font-mono border ${
                  scan.modules_completed.includes(m)
                    ? "bg-green-500/10 border-green-500/30 text-green-300"
                    : "bg-background/40 border-border/40 text-muted-foreground"
                }`}
              >
                {scan.modules_completed.includes(m) ? "✓ " : ""}
                {m}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Severity summary cards ── */}
      {scan.findings.length > 0 && (
        <div className="grid grid-cols-5 gap-2">
          {(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] as const).map(
            (sev) => {
              const count = severityCounts[sev] || 0;
              const c = SEV[sev];
              return (
                <button
                  key={sev}
                  onClick={() =>
                    setSeverityFilter(severityFilter === sev ? "" : sev)
                  }
                  className={`p-3 rounded-xl border text-center transition-all ${
                    severityFilter === sev
                      ? `${c.border} ${c.bg}`
                      : "border-white/[0.08] bg-background/40 hover:border-white/20"
                  }`}
                >
                  <p
                    className={`text-2xl font-black ${count > 0 ? c.text : "text-muted-foreground/40"}`}
                  >
                    {count}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">{sev}</p>
                </button>
              );
            },
          )}
        </div>
      )}

      {/* ── Findings list ── */}
      {scan.findings.length > 0 ? (
        <div className="space-y-3">
          {/* Filters */}
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2 flex-1">
              <Filter className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <span className="text-xs text-muted-foreground">
                {filtered.length} of {scan.findings.length} findings
                {severityFilter && ` · ${severityFilter}`}
                {moduleFilter && ` · ${moduleFilter}`}
              </span>
            </div>
            <div className="flex gap-2 flex-wrap">
              {modules.map((m) => (
                <button
                  key={m}
                  onClick={() => setModuleFilter(moduleFilter === m ? "" : m)}
                  className={`px-2.5 py-1 rounded-full text-xs font-mono border transition-all ${
                    moduleFilter === m
                      ? "bg-blue-500/20 border-blue-500/50 text-blue-300"
                      : "bg-background/40 border-border/40 text-muted-foreground hover:border-blue-500/30"
                  }`}
                >
                  {m}
                </button>
              ))}
              {(severityFilter || moduleFilter) && (
                <button
                  onClick={() => {
                    setSeverityFilter("");
                    setModuleFilter("");
                  }}
                  className="px-2.5 py-1 rounded-full text-xs border border-border/40 text-muted-foreground hover:text-foreground transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {filtered.map((f, i) => (
            <motion.div
              key={f.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <FindingCard f={f} defaultOpen={scan.findings.length === 1} />
            </motion.div>
          ))}
          {filtered.length === 0 && (
            <p className="text-center text-muted-foreground text-sm py-8">
              No findings match the current filters.
            </p>
          )}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 gap-3 bg-background/30 border border-white/[0.06] rounded-xl">
          <CheckCircle className="h-10 w-10 text-green-400" />
          <p className="text-sm font-medium text-foreground">
            No findings detected
          </p>
          <p className="text-xs text-muted-foreground">
            This scan completed with zero vulnerabilities.
          </p>
        </div>
      )}
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// PANELS
// ═══════════════════════════════════════════════════════════════════════════════

// ─── Panel: List Modules ──────────────────────────────────────────────────────

function ListModulesPanel() {
  const [modules, setModules] = useState<
    { name: string; description: string }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      setModules(await api.listModules());
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Scanner Modules</h2>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw
            className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      {loading ? (
        <Spinner text="Fetching modules…" />
      ) : (
        <div className="grid gap-2">
          {modules.map((m) => (
            <div
              key={m.name}
              className="flex items-start gap-3 p-3.5 bg-background/40 border border-white/[0.08] rounded-lg hover:border-blue-500/30 transition-colors"
            >
              <div className="p-1.5 bg-blue-500/10 rounded-md shrink-0">
                <Shield className="h-3.5 w-3.5 text-blue-400" />
              </div>
              <div>
                <p className="font-mono text-sm font-semibold text-foreground">
                  {m.name}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {m.description}
                </p>
              </div>
            </div>
          ))}
          {!loading && modules.length === 0 && (
            <p className="text-center text-muted-foreground py-8 text-sm">
              No modules found.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Panel: Queue a Scan ──────────────────────────────────────────────────────

function QueueScanPanel({
  onScanQueued,
}: {
  onScanQueued: (id: string) => void;
}) {
  const [modules, setModules] = useState<{ name: string }[]>([]);
  const [form, setForm] = useState({
    target_url: "",
    scan_type: "full",
    requester_name: "",
    organization: "",
    notes: "",
    consent_confirmed: false,
  });
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api
      .listModules()
      .then(setModules)
      .catch(() => {});
  }, []);

  const toggle = (n: string) =>
    setSelectedModules((p) =>
      p.includes(n) ? p.filter((x) => x !== n) : [...p, n],
    );

  const inp =
    "w-full px-4 py-2.5 bg-background/60 border border-border rounded-lg focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-colors text-sm outline-none";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.consent_confirmed) {
      setErr("You must confirm consent before scanning.");
      return;
    }
    setLoading(true);
    setErr("");
    setSuccess("");
    try {
      const res = await api.queueScan({
        ...form,
        modules: selectedModules.length > 0 ? selectedModules : null,
      });
      setSuccess(`Scan queued! ID: ${res.scan_id}`);
      onScanQueued(res.scan_id);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-base font-semibold">Queue a New Scan</h2>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      {success && (
        <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-3 flex items-center gap-2.5">
          <CheckCircle className="h-4 w-4 text-green-400" />
          <p className="text-green-300 text-sm break-all">{success}</p>
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="sm:col-span-2">
          <label className="block text-xs text-muted-foreground mb-1">
            Target URL *
          </label>
          <input
            className={inp}
            type="url"
            required
            placeholder="https://example.com"
            value={form.target_url}
            onChange={(e) => setForm({ ...form, target_url: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Scan Type
          </label>
          <select
            className={inp}
            value={form.scan_type}
            onChange={(e) => setForm({ ...form, scan_type: e.target.value })}
          >
            <option value="full">Full</option>
            <option value="quick">Quick</option>
            <option value="targeted">Targeted</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Requester Name *
          </label>
          <input
            className={inp}
            required
            placeholder="Alice Smith"
            value={form.requester_name}
            onChange={(e) =>
              setForm({ ...form, requester_name: e.target.value })
            }
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Organization *
          </label>
          <input
            className={inp}
            required
            placeholder="Acme Corp"
            value={form.organization}
            onChange={(e) => setForm({ ...form, organization: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Notes
          </label>
          <input
            className={inp}
            placeholder="Optional"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </div>
      </div>
      {form.scan_type === "targeted" && modules.length > 0 && (
        <div>
          <label className="block text-xs text-muted-foreground mb-2">
            Select Modules
          </label>
          <div className="flex flex-wrap gap-1.5">
            {modules.map((m) => (
              <button
                key={m.name}
                type="button"
                onClick={() => toggle(m.name)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono border transition-all ${selectedModules.includes(m.name) ? "bg-blue-500/20 border-blue-500/60 text-blue-300" : "bg-background/40 border-border text-muted-foreground hover:border-blue-500/40"}`}
              >
                {m.name}
              </button>
            ))}
          </div>
        </div>
      )}
      <label className="flex items-center gap-2.5 cursor-pointer">
        <input
          type="checkbox"
          checked={form.consent_confirmed}
          onChange={(e) =>
            setForm({ ...form, consent_confirmed: e.target.checked })
          }
          className="w-4 h-4 accent-blue-500 rounded"
        />
        <span className="text-xs text-muted-foreground">
          I confirm I have authorization to scan this target.
        </span>
      </label>
      <Button
        variant="purple"
        type="submit"
        size="lg"
        className="w-full"
        disabled={loading}
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Queuing…
          </>
        ) : (
          <>
            <Play className="mr-2 h-4 w-4" />
            Queue Scan
          </>
        )}
      </Button>
    </form>
  );
}

// ─── Panel: Poll Scan Status ──────────────────────────────────────────────────

function PollScanStatusPanel({ initialScanId }: { initialScanId?: string }) {
  const [scanId, setScanId] = useState(initialScanId ?? "");
  const [scan, setScan] = useState<ScanData | null>(null);
  const [polling, setPolling] = useState(false);
  const [err, setErr] = useState("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = () => {
    if (timer.current) clearInterval(timer.current);
    timer.current = null;
    setPolling(false);
  };

  const doPoll = useCallback(async (id: string) => {
    try {
      const data = await api.getScanStatus(id);
      setScan(data);
      if (data.status === "completed" || data.status === "failed") stop();
    } catch (e: any) {
      setErr(e.message);
      stop();
    }
  }, []);

  const start = () => {
    if (!scanId.trim()) {
      setErr("Enter a Scan ID.");
      return;
    }
    setErr("");
    setScan(null);
    setPolling(true);
    doPoll(scanId);
    timer.current = setInterval(() => doPoll(scanId), 4000);
  };

  useEffect(() => {
    if (initialScanId) {
      setScanId(initialScanId);
    }
    return () => stop();
  }, [initialScanId]);

  useEffect(() => {
    if (initialScanId?.trim()) start();
  }, [initialScanId]);

  const STEPS = ["queued", "running", "completed"];
  const stepIdx = scan ? STEPS.indexOf(scan.status) : -1;

  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold">Poll Scan Status</h2>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      <div className="flex gap-2">
        <input
          className="flex-1 px-4 py-2.5 bg-background/60 border border-border rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500/50 outline-none transition-colors"
          placeholder="Scan ID (UUID)"
          value={scanId}
          onChange={(e) => {
            setScanId(e.target.value);
            setScan(null);
          }}
        />
        <Button variant="purple" onClick={polling ? stop : start}>
          {polling ? (
            <>
              <X className="h-4 w-4 mr-1" />
              Stop
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-1" />
              Poll
            </>
          )}
        </Button>
      </div>

      {polling && !scan && <Spinner text="Fetching scan status…" />}

      {scan && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          {/* Progress stepper */}
          <div className="p-4 bg-background/40 border border-white/[0.08] rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium truncate mr-3">
                {scan.target_url}
              </span>
              <StatusBadge status={scan.status} />
            </div>
            <div className="flex items-center gap-2">
              {STEPS.map((step, i) => (
                <div key={step} className="flex items-center gap-2 flex-1">
                  <div
                    className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all ${i < stepIdx ? "bg-green-500 text-white" : i === stepIdx ? "bg-blue-500 text-white ring-2 ring-blue-500/30" : "bg-background border border-border/60 text-muted-foreground"}`}
                  >
                    {i < stepIdx ? "✓" : i + 1}
                  </div>
                  <span className="text-xs text-muted-foreground capitalize hidden sm:block">
                    {step}
                  </span>
                  {i < STEPS.length - 1 && (
                    <div
                      className={`flex-1 h-px ${i < stepIdx ? "bg-green-500" : "bg-border/40"}`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Full scan result once completed */}
          {scan.status === "completed" && <ScanResultView scan={scan} />}
          {scan.status === "failed" && scan.error_message && (
            <ErrBox
              msg={`Scan failed: ${scan.error_message}`}
              onClose={() => {}}
            />
          )}
          {polling &&
            scan.status !== "completed" &&
            scan.status !== "failed" && (
              <p className="text-xs text-muted-foreground text-center animate-pulse">
                Polling every 4 seconds…
              </p>
            )}
        </motion.div>
      )}
    </div>
  );
}

// ─── Panel: List All Scans ────────────────────────────────────────────────────

function ListAllScansPanel({
  onSelectScan,
}: {
  onSelectScan: (id: string) => void;
}) {
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      const r = await api.listScans(filter || undefined);
      setScans(r.scans);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [filter]);

  const doDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api.deleteScan(deleteTarget);
      setScans((p) => p.filter((s) => s.id !== deleteTarget));
      setDeleteTarget(null);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {deleteTarget && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <div className="bg-background border border-border rounded-xl p-6 max-w-sm w-full space-y-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                <h3 className="font-semibold">Delete Scan?</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                This will permanently delete the scan and all its findings.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setDeleteTarget(null)}
                >
                  Cancel
                </Button>
                <button
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center"
                  onClick={doDelete}
                  disabled={deleting}
                >
                  {deleting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    "Delete"
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-2 flex-wrap">
        <h2 className="text-base font-semibold flex-1">All Scans</h2>
        <select
          className="px-3 py-2 bg-background/60 border border-border rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500/50"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          {["queued", "running", "completed", "failed"].map((s) => (
            <option key={s} value={s}>
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </option>
          ))}
        </select>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw
            className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      {loading ? (
        <Spinner text="Loading scans…" />
      ) : (
        <div className="space-y-2.5">
          {scans.map((s) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-4 bg-background/40 border border-white/[0.08] rounded-xl hover:border-blue-500/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{s.target_url}</p>
                  <p className="text-xs font-mono text-muted-foreground mt-0.5 truncate">
                    {s.id}
                  </p>
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <StatusBadge status={s.status} />
                    <span className="text-xs text-muted-foreground">
                      {s.organization}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex gap-1.5 mt-2 flex-wrap">
                    {s.critical > 0 && (
                      <span className="px-1.5 py-0.5 bg-red-600/15 text-red-400 text-xs rounded border border-red-500/30">
                        C:{s.critical}
                      </span>
                    )}
                    {s.high > 0 && (
                      <span className="px-1.5 py-0.5 bg-orange-500/15 text-orange-400 text-xs rounded border border-orange-500/30">
                        H:{s.high}
                      </span>
                    )}
                    {s.medium > 0 && (
                      <span className="px-1.5 py-0.5 bg-yellow-500/15 text-yellow-400 text-xs rounded border border-yellow-500/30">
                        M:{s.medium}
                      </span>
                    )}
                    {s.low > 0 && (
                      <span className="px-1.5 py-0.5 bg-blue-500/15 text-blue-400 text-xs rounded border border-blue-500/30">
                        L:{s.low}
                      </span>
                    )}
                    {s.total_findings === 0 && (
                      <span className="text-xs text-muted-foreground">
                        Clean ✓
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-1.5 shrink-0">
                  {s.status === "completed" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onSelectScan(s.id)}
                      title="View Report"
                    >
                      <FileText className="h-3.5 w-3.5" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setDeleteTarget(s.id)}
                    className="hover:bg-red-900/30 hover:border-red-500/50 hover:text-red-400"
                    title="Delete"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
          {scans.length === 0 && (
            <p className="text-center text-muted-foreground py-12 text-sm">
              No scans found.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Panel: Get Findings (filtered, with full cards) ──────────────────────────

function GetFindingsPanel({ initialScanId }: { initialScanId?: string }) {
  const [scanId, setScanId] = useState(initialScanId ?? "");
  const [severity, setSeverity] = useState("");
  const [module, setModule] = useState("");
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (initialScanId) setScanId(initialScanId);
  }, [initialScanId]);

  const load = async () => {
    if (!scanId.trim()) {
      setErr("Enter a Scan ID.");
      return;
    }
    setLoading(true);
    setErr("");
    try {
      const r = await api.getFindings(
        scanId,
        severity || undefined,
        module || undefined,
      );
      setFindings(r.findings);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold">Get Findings</h2>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Scan ID
          </label>
          <input
            className="w-full px-3 py-2.5 bg-background/60 border border-border rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500/50 outline-none"
            placeholder="UUID"
            value={scanId}
            onChange={(e) => setScanId(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Severity
          </label>
          <select
            className="w-full px-3 py-2.5 bg-background/60 border border-border rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 outline-none"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          >
            <option value="">All</option>
            {["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-muted-foreground mb-1">
            Module
          </label>
          <input
            className="w-full px-3 py-2.5 bg-background/60 border border-border rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 outline-none"
            placeholder="e.g. xss"
            value={module}
            onChange={(e) => setModule(e.target.value)}
          />
        </div>
      </div>
      <Button
        variant="purple"
        onClick={load}
        disabled={loading}
        className="w-full"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
        ) : (
          <Filter className="h-4 w-4 mr-2" />
        )}
        Fetch Findings
      </Button>
      {findings.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            {findings.length} finding(s)
          </p>
          {findings.map((f) => (
            <FindingCard key={f.id} f={f} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Panel: Full Report ───────────────────────────────────────────────────────

function FullReportPanel({ initialScanId }: { initialScanId?: string }) {
  const [scanId, setScanId] = useState(initialScanId ?? "");
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (initialScanId) setScanId(initialScanId);
  }, [initialScanId]);

  const load = async () => {
    if (!scanId.trim()) {
      setErr("Enter a Scan ID.");
      return;
    }
    setLoading(true);
    setErr("");
    setReport(null);
    try {
      setReport(await api.getReport(scanId));
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  const riskCls = (s: number) =>
    s >= 8 ? "text-red-400" : s >= 5 ? "text-orange-400" : "text-green-400";

  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold">Full Report</h2>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      <div className="flex gap-2">
        <input
          className="flex-1 px-4 py-2.5 bg-background/60 border border-border rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500/50 outline-none"
          placeholder="Scan ID (UUID)"
          value={scanId}
          onChange={(e) => setScanId(e.target.value)}
        />
        <Button variant="purple" onClick={load} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <FileText className="h-4 w-4" />
          )}
        </Button>
      </div>
      {loading && <Spinner text="Generating report…" />}
      {report && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <div className="p-5 bg-background/40 border border-white/[0.08] rounded-xl flex items-center gap-6">
            <div className="text-center shrink-0">
              <p
                className={`text-5xl font-black ${riskCls(report.risk_score)}`}
              >
                {report.risk_score.toFixed(1)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Risk Score</p>
            </div>
            <div className="flex-1 space-y-2">
              <p className="text-sm font-medium break-all">
                {report.target_url}
              </p>
              <p className="text-xs text-muted-foreground">
                {report.organization} · {report.scan_type}
              </p>
              <div className="w-full bg-white/10 rounded-full h-1.5">
                <motion.div
                  className={`h-1.5 rounded-full ${report.risk_score >= 8 ? "bg-red-500" : report.risk_score >= 5 ? "bg-orange-500" : "bg-green-500"}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${(report.risk_score / 10) * 100}%` }}
                  transition={{ duration: 0.8 }}
                />
              </div>
            </div>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {Object.entries(report.severity_summary).map(([sev, count]) => {
              const c = SEV[sev] ?? SEV.INFO;
              return (
                <div
                  key={sev}
                  className={`p-3 rounded-xl border ${c.border} ${c.bg} text-center`}
                >
                  <p className={`text-xl font-black ${c.text}`}>{count}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{sev}</p>
                </div>
              );
            })}
          </div>
          {report.gemini_insight && (
            <div className="p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl">
              <p className="text-xs font-semibold text-blue-400 mb-2 flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5" />
                AI Insight
              </p>
              <p className="text-sm text-foreground/90">
                {report.gemini_insight}
              </p>
            </div>
          )}
          {report.priority_findings?.length > 0 && (
            <div>
              <p className="text-sm font-semibold mb-3">Priority Findings</p>
              <div className="space-y-2">
                {report.priority_findings.map((f) => (
                  <FindingCard key={f.id} f={f} />
                ))}
              </div>
            </div>
          )}
          <div>
            <p className="text-xs text-muted-foreground mb-2">Modules Run</p>
            <div className="flex flex-wrap gap-1.5">
              {report.modules_run?.map((m) => (
                <span
                  key={m}
                  className="px-2 py-0.5 bg-background/60 border border-border/40 rounded text-xs font-mono text-muted-foreground"
                >
                  {m}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

// ─── Panel: Analytics ─────────────────────────────────────────────────────────

function AnalyticsPanel() {
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const load = async () => {
    setLoading(true);
    setErr("");
    try {
      setData(await api.getAnalytics());
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Platform Analytics</h2>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw
            className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      {loading ? (
        <Spinner text="Loading analytics…" />
      ) : (
        data && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-2 gap-3">
              {(
                [
                  {
                    label: "Total Scans",
                    value: data.total_scans,
                    icon: <Target className="h-5 w-5 text-blue-400" />,
                  },
                  {
                    label: "Completed",
                    value: data.completed_scans,
                    icon: <CheckCircle className="h-5 w-5 text-green-400" />,
                  },
                  {
                    label: "Total Findings",
                    value: data.total_findings,
                    icon: <AlertTriangle className="h-5 w-5 text-orange-400" />,
                  },
                  {
                    label: "Orgs Scanned",
                    value: data.orgs_scanned,
                    icon: <Shield className="h-5 w-5 text-purple-400" />,
                  },
                ] as const
              ).map(({ label, value, icon }) => (
                <div
                  key={label}
                  className="p-4 bg-background/40 border border-white/[0.08] rounded-xl"
                >
                  <div className="flex items-center justify-between mb-2">
                    {icon}
                    <span className="text-2xl font-black">{value}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{label}</p>
                </div>
              ))}
            </div>
            <div className="p-4 bg-background/40 border border-white/[0.08] rounded-xl space-y-3">
              <p className="text-sm font-semibold">Severity Breakdown</p>
              {(["critical", "high", "medium", "low"] as const).map((k) => {
                const val = data.severity_breakdown[k] ?? 0;
                const pct =
                  data.total_findings > 0
                    ? (val / data.total_findings) * 100
                    : 0;
                const colors: Record<string, string> = {
                  critical: "bg-red-500",
                  high: "bg-orange-500",
                  medium: "bg-yellow-500",
                  low: "bg-blue-500",
                };
                return (
                  <div key={k}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground capitalize">
                        {k}
                      </span>
                      <span className="font-medium">{val}</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-1.5">
                      <motion.div
                        className={`h-1.5 rounded-full ${colors[k]}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )
      )}
    </div>
  );
}

// ─── Panel: Delete Scan ───────────────────────────────────────────────────────

function DeleteScanPanel() {
  const [scanId, setScanId] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");
  const [confirm, setConfirm] = useState(false);

  const doDelete = async () => {
    if (!confirm) {
      setConfirm(true);
      return;
    }
    setLoading(true);
    setErr("");
    setSuccess("");
    try {
      await api.deleteScan(scanId);
      setSuccess(`Scan ${scanId} deleted.`);
      setScanId("");
      setConfirm(false);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-base font-semibold">Delete a Scan</h2>
      {err && <ErrBox msg={err} onClose={() => setErr("")} />}
      {success && (
        <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-3 flex items-center gap-2.5">
          <CheckCircle className="h-4 w-4 text-green-400" />
          <p className="text-green-300 text-sm break-all">{success}</p>
        </div>
      )}
      <div>
        <label className="block text-xs text-muted-foreground mb-1.5">
          Scan ID to Delete
        </label>
        <input
          className="w-full px-4 py-2.5 bg-background/60 border border-border rounded-lg text-sm font-mono focus:ring-2 focus:ring-blue-500/50 outline-none"
          placeholder="UUID"
          value={scanId}
          onChange={(e) => {
            setScanId(e.target.value);
            setConfirm(false);
          }}
        />
      </div>
      {confirm && (
        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-3">
          <p className="text-red-300 text-sm font-medium">⚠️ Are you sure?</p>
          <p className="text-red-400 text-xs mt-0.5">
            Click Delete again to confirm permanent deletion.
          </p>
        </div>
      )}
      <button
        onClick={doDelete}
        disabled={loading || !scanId.trim()}
        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Trash2 className="h-4 w-4" />
        )}
        {confirm ? "Confirm Delete" : "Delete Scan"}
      </button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════════════════════════════════════════════

const PANELS = [
  {
    id: "list-modules",
    label: "List Modules",
    icon: <List className="h-4 w-4" />,
  },
  {
    id: "queue-scan",
    label: "Queue a Scan",
    icon: <Play className="h-4 w-4" />,
  },
  {
    id: "poll-status",
    label: "Poll Scan Status",
    icon: <RefreshCw className="h-4 w-4" />,
  },
  {
    id: "list-scans",
    label: "List All Scans",
    icon: <Search className="h-4 w-4" />,
  },
  {
    id: "findings",
    label: "Get Findings",
    icon: <Filter className="h-4 w-4" />,
  },
  {
    id: "report",
    label: "Full Report",
    icon: <FileText className="h-4 w-4" />,
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: <BarChart3 className="h-4 w-4" />,
  },
  {
    id: "delete",
    label: "Delete a Scan",
    icon: <Trash2 className="h-4 w-4" />,
  },
] as const;

type PanelId = (typeof PANELS)[number]["id"];

export default function IntrusionTestPage() {
  const [active, setActive] = useState<PanelId>("queue-scan");
  const [ddOpen, setDdOpen] = useState(false);
  const [activeScanId, setActiveScanId] = useState<string | undefined>(
    undefined,
  );
  const ddRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ddRef.current && !ddRef.current.contains(e.target as Node))
        setDdOpen(false);
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, []);

  const onScanQueued = (id: string) => {
    setActiveScanId(id);
    setActive("poll-status");
  };
  const onSelectScan = (id: string) => {
    setActiveScanId(id);
    setActive("report");
  };

  const panel = PANELS.find((p) => p.id === active)!;

  const renderPanel = () => {
    switch (active) {
      case "list-modules":
        return <ListModulesPanel />;
      case "queue-scan":
        return <QueueScanPanel onScanQueued={onScanQueued} />;
      case "poll-status":
        return <PollScanStatusPanel initialScanId={activeScanId} />;
      case "list-scans":
        return <ListAllScansPanel onSelectScan={onSelectScan} />;
      case "findings":
        return <GetFindingsPanel initialScanId={activeScanId} />;
      case "report":
        return <FullReportPanel initialScanId={activeScanId} />;
      case "analytics":
        return <AnalyticsPanel />;
      case "delete":
        return <DeleteScanPanel />;
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden p-6 sm:p-10">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <FlickeringGrid
          className="w-full h-full"
          squareSize={4}
          gridGap={6}
          flickerChance={0.05}
          color="rgb(59, 130, 246)"
          maxOpacity={0.8}
        />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto">
        {/* Nav */}
        <div className="mb-8 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold gradient-text">
            CognitoForge
          </Link>
          <Link
            href="/demo"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Dashboard
          </Link>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="text-center mb-7">
            <h1 className="text-3xl font-bold mb-2">
              Intrusion <span className="gradient-text">Test</span>
            </h1>
            <p className="text-muted-foreground text-sm">
              Vulnerability scanning powered by VulnScan API · localhost:8000
            </p>
          </div>

          {/* Dropdown switcher */}
          <div className="mb-4 relative" ref={ddRef}>
            <button
              onClick={() => setDdOpen(!ddOpen)}
              className="w-full flex items-center justify-between px-4 py-3.5 glass border border-white/10 rounded-xl hover:border-blue-500/40 transition-all text-sm font-medium"
            >
              <span className="flex items-center gap-2.5">
                <span className="text-blue-400">{panel.icon}</span>
                {panel.label}
              </span>
              <ChevronDown
                className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${ddOpen ? "rotate-180" : ""}`}
              />
            </button>

            <AnimatePresence>
              {ddOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -6, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -6, scale: 0.98 }}
                  transition={{ duration: 0.12 }}
                  className="absolute top-full mt-2 w-full glass border border-white/10 rounded-xl overflow-hidden z-50 shadow-2xl"
                >
                  {PANELS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => {
                        setActive(p.id);
                        setDdOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-4 py-3 text-sm text-left transition-colors hover:bg-blue-500/10 ${active === p.id ? "bg-blue-500/15 text-blue-300 font-medium" : "text-foreground/80"}`}
                    >
                      <span
                        className={
                          active === p.id
                            ? "text-blue-400"
                            : "text-muted-foreground"
                        }
                      >
                        {p.icon}
                      </span>
                      {p.label}
                      {active === p.id && (
                        <CheckCircle className="h-3.5 w-3.5 text-blue-400 ml-auto" />
                      )}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Active scan ID pill */}
          {activeScanId && (
            <div className="mb-4 flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <Info className="h-3.5 w-3.5 text-blue-400 shrink-0" />
              <span className="text-xs text-muted-foreground">
                Active scan:
              </span>
              <span className="text-xs font-mono text-blue-300 truncate flex-1">
                {activeScanId}
              </span>
              <button onClick={() => setActiveScanId(undefined)}>
                <X className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground" />
              </button>
            </div>
          )}

          {/* Panel */}
          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.18 }}
              className="glass p-6 rounded-xl border border-white/10"
            >
              {renderPanel()}
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
