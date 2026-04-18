"use client";

import Link from "next/link";
import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Loader2,
  Download,
  Shield,
  Zap,
  Target,
  AlertTriangle,
  XCircle,
  BarChart2,
  X,
  RefreshCw,
  Activity,
  Lock,
  Eye,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

type ModuleType = "vulnerability" | "performance" | "intrusion";

interface ScanItem {
  id: string;
  label: string;
  meta?: string;
}

// Vulnerability Scan — affected_files + ai_insights (AI red-team MITRE simulation)
interface VulnReport {
  repo_id: string;
  run_id: string;
  timestamp?: string;
  summary: {
    overall_severity: string;
    affected_files: string[];
    [key: string]: unknown;
  };
  ai_insight?: string;
}

// Performance Test — performance_runs (k6)
interface PerfReport {
  run_id: string;
  target_url: string;
  test_type: string;
  duration: string;
  vus_max: number;
  created_at?: string;
  metrics: {
    requests: {
      total: number;
      successful?: number;
      failed?: number;
      failed_rate: number;
      success_rate?: number;
    };
    response_time: {
      avg: number;
      min: number;
      max: number;
      p50?: number;
      p95: number;
      p99: number;
    };
    virtual_users: { max: number; avg: number };
  };
  performance_summary?: {
    status: string;
    bottlenecks: string[];
    recommendations: string[];
  };
}

// Intrusion Test — vulnscan_scans + vulnscan_findings (passive web scanner)
interface IntrusionFinding {
  id: string;
  title: string;
  severity: string;
  module: string;
  description: string;
  remediation: string;
  cvss_score?: number;
  cve_id?: string;
  cwe_id?: string;
  evidence?: string;
  affected_url?: string;
}
interface IntrusionReport {
  scan_id: string;
  target_url: string;
  organization: string;
  scan_type: string;
  status?: string;
  risk_score: number;
  severity_summary: Record<string, number>;
  priority_findings: IntrusionFinding[];
  all_findings: IntrusionFinding[];
  modules_run: string[];
  completed_at?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const MODULE_CFG = {
  vulnerability: {
    label: "Vulnerability Scan",
    subtitle: "AI red-team MITRE ATT&CK simulation",
    icon: Shield,
    grad: "from-rose-500/20 to-orange-500/10",
    accent: "text-rose-400",
  },
  performance: {
    label: "Performance Test",
    subtitle: "k6 load / stress / spike / smoke",
    icon: Zap,
    grad: "from-amber-500/20 to-yellow-500/10",
    accent: "text-amber-400",
  },
  intrusion: {
    label: "Intrusion Test",
    subtitle: "Passive web scanner — XSS, SQLi, headers",
    icon: Target,
    grad: "from-violet-500/20 to-purple-500/10",
    accent: "text-violet-400",
  },
} as const;

const SEV_CLS: Record<string, string> = {
  CRITICAL: "text-red-400 bg-red-400/10 border-red-400/30",
  HIGH: "text-orange-400 bg-orange-400/10 border-orange-400/30",
  MEDIUM: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  LOW: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  INFO: "text-sky-400 bg-sky-400/10 border-sky-400/30",
  critical: "text-red-400 bg-red-400/10 border-red-400/30",
  high: "text-orange-400 bg-orange-400/10 border-orange-400/30",
  medium: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  low: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  unknown: "text-slate-400 bg-slate-400/10 border-slate-400/30",
};

// ─────────────────────────────────────────────────────────────────────────────
// API
// ─────────────────────────────────────────────────────────────────────────────

async function loadScans(module: ModuleType): Promise<ScanItem[]> {
  if (module === "vulnerability") {
    const d = await fetch(
      `${API_BASE}/api/reports/vulnerability?limit=50`,
    ).then((r) => r.json());
    return (d.scans ?? []).map((s: Record<string, unknown>) => ({
      id: s.run_id as string,
      label: `${s.repo_id} — ${s.run_id}`,
      meta: `${s.dominant_severity} severity · ${s.total_files} files · ${s.timestamp ?? ""}`,
    }));
  }
  if (module === "performance") {
    const d = await fetch(`${API_BASE}/api/reports/performance?limit=50`).then(
      (r) => r.json(),
    );
    return (d.runs ?? []).map((r: Record<string, unknown>) => ({
      id: r.run_id as string,
      label: r.target_url as string,
      meta: `${r.test_type} · ${r.duration} · ${r.vus_max} VUs`,
    }));
  }
  // intrusion
  const d = await fetch(`${API_BASE}/api/reports/intrusion?limit=50`).then(
    (r) => r.json(),
  );
  return (d.scans ?? []).map((s: Record<string, unknown>) => ({
    id: s.id as string,
    label: s.target_url as string,
    meta: `${s.status} · ${s.scan_type} · ${s.total_findings} findings`,
  }));
}

async function loadReport(module: ModuleType, id: string) {
  const url =
    module === "vulnerability"
      ? `${API_BASE}/api/reports/vulnerability/${id}`
      : module === "performance"
        ? `${API_BASE}/api/reports/performance/${id}`
        : `${API_BASE}/api/reports/intrusion/${id}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ─────────────────────────────────────────────────────────────────────────────
// PDF via print window
// ─────────────────────────────────────────────────────────────────────────────

function openPDF(html: string, title: string) {
  const win = window.open("", "_blank");
  if (!win) {
    alert("Allow popups to download the PDF.");
    return;
  }
  win.document.write(`<!DOCTYPE html><html><head>
<meta charset="UTF-8"/>
<title>${title}</title>
<style>
  @page { margin: 20mm; }
  * { box-sizing: border-box; }
  body { font-family: Arial, sans-serif; font-size: 12px; color: #1a1a2e; background: #fff; margin: 0; }
  h1 { font-size: 22px; color: #1e1b4b; border-bottom: 3px solid #6d28d9; padding-bottom: 8px; margin-bottom: 4px; }
  h2 { font-size: 15px; color: #4c1d95; margin-top: 20px; margin-bottom: 6px; border-left: 4px solid #7c3aed; padding-left: 8px; }
  .meta { color: #6b7280; font-size: 11px; margin: 2px 0; }
  .grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin: 12px 0; }
  .card { background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 6px; padding: 10px 14px; }
  .card .val { font-size: 22px; font-weight: bold; color: #5b21b6; }
  .card .lbl { font-size: 10px; color: #7c3aed; margin-top: 2px; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 11px; }
  th { background: #ede9fe; color: #4c1d95; padding: 6px 8px; border: 1px solid #c4b5fd; text-align: left; }
  td { padding: 5px 8px; border: 1px solid #e5e7eb; vertical-align: top; }
  tr:nth-child(even) td { background: #faf5ff; }
  .badge { display:inline-block; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:bold; }
  .CRITICAL,.critical { background:#fee2e2; color:#991b1b; }
  .HIGH,.high         { background:#ffedd5; color:#9a3412; }
  .MEDIUM,.medium     { background:#fef9c3; color:#854d0e; }
  .LOW,.low           { background:#dcfce7; color:#166534; }
  .INFO               { background:#e0f2fe; color:#0c4a6e; }
  .insight { background:#f5f3ff; border-left:4px solid #7c3aed; padding:10px 14px; border-radius:4px; margin:10px 0; font-style:italic; line-height:1.6; }
  .files { font-family: monospace; font-size:10px; background:#f8fafc; padding:10px; border-radius:4px; line-height:1.8; border:1px solid #e2e8f0; }
  .bar-row { display:flex; align-items:center; gap:8px; margin:4px 0; }
  .bar-track { flex:1; background:#ede9fe; border-radius:4px; height:8px; }
  .bar-fill { height:8px; border-radius:4px; background:#7c3aed; }
  .bar-label { width:32px; font-size:10px; color:#6b7280; }
  .bar-val { width:60px; font-size:10px; text-align:right; }
  .status-box { padding:8px 14px; border-radius:6px; font-weight:bold; font-size:12px; margin:8px 0; }
  .footer { margin-top:32px; padding-top:12px; border-top:1px solid #e5e7eb; color:#9ca3af; font-size:10px; }
  @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
</style>
</head><body>${html}
<div class="footer">Generated by CognitoForge Labs · ${new Date().toLocaleString()}</div>
<script>window.onload=()=>{window.print();}</script>
</body></html>`);
  win.document.close();
}

function buildVulnPDF(r: VulnReport) {
  const sev = r.summary ?? {};
  const files = (sev.affected_files as string[]) ?? [];
  const sevKeys = ["critical", "high", "medium", "low", "unknown"].filter(
    (k) => (sev[`${k}_steps`] as number) > 0,
  );

  const sevRows = sevKeys
    .map(
      (k) =>
        `<tr><td><span class="badge ${k}">${k.toUpperCase()}</span></td><td>${sev[`${k}_steps`]}</td></tr>`,
    )
    .join("");

  const fileRows = files
    .slice(0, 50)
    .map((f) => `<div>${f}</div>`)
    .join("");

  return `
<h1>🛡 Vulnerability Scan Report</h1>
<p class="meta"><b>Repo:</b> ${r.repo_id}</p>
<p class="meta"><b>Run ID:</b> ${r.run_id}</p>
<p class="meta"><b>Timestamp:</b> ${r.timestamp ?? "—"}</p>

<h2>Overall Severity</h2>
<p><span class="badge ${r.summary.overall_severity}" style="font-size:16px;padding:4px 14px;">
  ${(r.summary.overall_severity ?? "unknown").toUpperCase()}
</span></p>

${r.ai_insight ? `<h2>AI Security Insight</h2><div class="insight">${r.ai_insight}</div>` : ""}

<h2>Severity Breakdown</h2>
<table><tr><th>Severity</th><th>Count</th></tr>${sevRows}</table>

<h2>Affected Files (${files.length})</h2>
<div class="files">${fileRows || "None recorded"}</div>
`;
}

function buildPerfPDF(r: PerfReport) {
  const rt = r.metrics?.response_time ?? {};
  const req = r.metrics?.requests ?? {};
  const vu = r.metrics?.virtual_users ?? {};
  const maxMs = rt.max || 1;

  const bars = [
    { l: "Avg", v: rt.avg ?? 0 },
    { l: "P50", v: (rt as Record<string, number>).p50 ?? 0 },
    { l: "P95", v: rt.p95 ?? 0 },
    { l: "P99", v: rt.p99 ?? 0 },
    { l: "Max", v: rt.max ?? 0 },
  ]
    .map((b) => {
      const pct = Math.min(100, (b.v / maxMs) * 100).toFixed(1);
      return `<div class="bar-row">
      <span class="bar-label">${b.l}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <span class="bar-val">${Math.round(b.v)} ms</span>
    </div>`;
    })
    .join("");

  const ps = r.performance_summary;
  const statusColor = (ps?.status ?? "").includes("CRITICAL")
    ? "#fee2e2"
    : (ps?.status ?? "").includes("WARNING")
      ? "#fef9c3"
      : (ps?.status ?? "").includes("EXCELLENT")
        ? "#dcfce7"
        : "#ede9fe";

  return `
<h1>⚡ Performance Test Report</h1>
<p class="meta"><b>Target:</b> ${r.target_url}</p>
<p class="meta"><b>Test Type:</b> ${r.test_type} · <b>Duration:</b> ${r.duration} · <b>Max VUs:</b> ${r.vus_max}</p>
<p class="meta"><b>Run ID:</b> ${r.run_id}</p>
<p class="meta"><b>Timestamp:</b> ${r.created_at ?? "—"}</p>

<h2>Key Metrics</h2>
<div class="grid">
  <div class="card"><div class="val">${(req.total ?? 0).toLocaleString()}</div><div class="lbl">Total Requests</div></div>
  <div class="card"><div class="val">${(req.success_rate ?? 100 - (req.failed_rate ?? 0)).toFixed(1)}%</div><div class="lbl">Success Rate</div></div>
  <div class="card"><div class="val">${Math.round(rt.avg ?? 0)} ms</div><div class="lbl">Avg Response</div></div>
  <div class="card"><div class="val">${Math.round(rt.p95 ?? 0)} ms</div><div class="lbl">P95 Latency</div></div>
  <div class="card"><div class="val">${Math.round(rt.p99 ?? 0)} ms</div><div class="lbl">P99 Latency</div></div>
  <div class="card"><div class="val">${vu.max ?? r.vus_max}</div><div class="lbl">Peak VUs</div></div>
</div>

<h2>Response Time Distribution</h2>
${bars}

${
  ps
    ? `
<h2>Assessment</h2>
<div class="status-box" style="background:${statusColor}">${ps.status}</div>
<h2>Bottlenecks</h2>
<table><tr><th>Issue</th></tr>${ps.bottlenecks.map((b) => `<tr><td>${b}</td></tr>`).join("")}</table>
<h2>Recommendations</h2>
<table><tr><th>Action</th></tr>${ps.recommendations.map((b) => `<tr><td>${b}</td></tr>`).join("")}</table>
`
    : ""
}
`;
}

function buildIntrusionPDF(r: IntrusionReport) {
  const sev = r.severity_summary ?? {};
  const sevRows = Object.entries(sev)
    .filter(([, v]) => v > 0)
    .map(
      ([k, v]) =>
        `<tr><td><span class="badge ${k}">${k}</span></td><td>${v}</td></tr>`,
    )
    .join("");

  const findingRows = (r.all_findings ?? [])
    .slice(0, 40)
    .map(
      (f) => `
    <tr>
      <td><span class="badge ${f.severity}">${f.severity}</span></td>
      <td>${f.module}</td>
      <td>${f.title}</td>
      <td style="font-size:10px">${f.remediation?.slice(0, 100) ?? "—"}…</td>
    </tr>`,
    )
    .join("");

  return `
<h1>🎯 Intrusion Test Report</h1>
<p class="meta"><b>Target:</b> ${r.target_url}</p>
<p class="meta"><b>Organization:</b> ${r.organization ?? "—"}</p>
<p class="meta"><b>Scan Type:</b> ${r.scan_type} · <b>Status:</b> ${r.status ?? "—"}</p>
<p class="meta"><b>Modules run:</b> ${(r.modules_run ?? []).join(", ") || "—"}</p>
<p class="meta"><b>Completed:</b> ${r.completed_at ?? "—"}</p>

<h2>Risk Score</h2>
<div class="card" style="display:inline-block;min-width:120px">
  <div class="val">${r.risk_score}/10</div>
  <div class="lbl">Overall Risk</div>
</div>

<h2>Severity Summary</h2>
<table><tr><th>Severity</th><th>Count</th></tr>${sevRows}</table>

<h2>Priority Findings (CRITICAL / HIGH)</h2>
<table>
  <tr><th>Severity</th><th>Module</th><th>Title</th><th>CVSS</th></tr>
  ${(r.priority_findings ?? [])
    .map(
      (f) => `<tr>
    <td><span class="badge ${f.severity}">${f.severity}</span></td>
    <td>${f.module}</td><td>${f.title}</td>
    <td>${f.cvss_score ?? "—"}</td>
  </tr>`,
    )
    .join("")}
</table>

<h2>All Findings (${(r.all_findings ?? []).length})</h2>
<table>
  <tr><th>Severity</th><th>Module</th><th>Title</th><th>Remediation</th></tr>
  ${findingRows}
</table>
`;
}

// ─────────────────────────────────────────────────────────────────────────────
// Small UI components
// ─────────────────────────────────────────────────────────────────────────────

function SevBadge({ sev }: { sev: string }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${SEV_CLS[sev] ?? SEV_CLS.unknown}`}
    >
      {sev}
    </span>
  );
}

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-white/5 rounded-lg border border-white/10 p-4">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Preview panels
// ─────────────────────────────────────────────────────────────────────────────

function VulnPreview({ r }: { r: VulnReport }) {
  const sev = r.summary ?? {};
  const files = (sev.affected_files as string[]) ?? [];
  const sevKeys = ["critical", "high", "medium", "low", "unknown"].filter(
    (k) => (sev[`${k}_steps`] as number) > 0,
  );
  const totalFiles = files.length;

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <StatCard
          label="Overall Severity"
          value={((sev.overall_severity as string) ?? "—").toUpperCase()}
        />
        <StatCard label="Affected Files" value={totalFiles} />
        <StatCard label="Severity Levels" value={sevKeys.length} />
      </div>

      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          Breakdown
        </p>
        <div className="flex flex-wrap gap-2">
          {sevKeys.map((k) => (
            <div key={k} className="flex items-center gap-1.5">
              <SevBadge sev={k} />
              <span className="text-sm font-medium">
                {sev[`${k}_steps`] as number}
              </span>
            </div>
          ))}
        </div>
      </div>

      {r.ai_insight && (
        <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-4">
          <p className="text-xs font-semibold text-violet-400 mb-2 flex items-center gap-1">
            <Lock className="h-3 w-3" /> AI Security Insight
          </p>
          <p className="text-sm text-slate-300 leading-relaxed">
            {r.ai_insight}
          </p>
        </div>
      )}

      {files.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Affected Files ({files.length})
          </p>
          <div className="bg-white/5 rounded-lg border border-white/10 p-3 max-h-36 overflow-y-auto">
            {files.map((f, i) => (
              <p key={i} className="text-xs font-mono text-slate-400 py-0.5">
                {f}
              </p>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        Repo: <span className="text-white font-mono">{r.repo_id}</span> · Run:{" "}
        <span className="font-mono">{r.run_id}</span>
      </p>
    </div>
  );
}

function PerfPreview({ r }: { r: PerfReport }) {
  const rt = r.metrics?.response_time ?? {};
  const req = r.metrics?.requests ?? {};
  const vu = r.metrics?.virtual_users ?? {};
  const maxMs = rt.max || 1;

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <StatCard
          label="Total Requests"
          value={(req.total ?? 0).toLocaleString()}
        />
        <StatCard
          label="Success Rate"
          value={`${(req.success_rate ?? 100 - (req.failed_rate ?? 0)).toFixed(1)}%`}
          sub={`${req.failed ?? 0} failed`}
        />
        <StatCard
          label="Avg Response"
          value={`${Math.round(rt.avg ?? 0)} ms`}
        />
        <StatCard label="P95 Latency" value={`${Math.round(rt.p95 ?? 0)} ms`} />
        <StatCard label="P99 Latency" value={`${Math.round(rt.p99 ?? 0)} ms`} />
        <StatCard
          label="Peak VUs"
          value={vu.max ?? r.vus_max ?? 0}
          sub={`avg ${(vu.avg ?? 0).toFixed(0)}`}
        />
      </div>

      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Response Time
        </p>
        {[
          { l: "Avg", v: rt.avg ?? 0, c: "bg-amber-400" },
          {
            l: "P50",
            v: (rt as Record<string, number>).p50 ?? 0,
            c: "bg-amber-300",
          },
          { l: "P95", v: rt.p95 ?? 0, c: "bg-orange-400" },
          { l: "P99", v: rt.p99 ?? 0, c: "bg-red-400" },
          { l: "Max", v: rt.max ?? 0, c: "bg-red-500" },
        ].map((b) => (
          <div key={b.l} className="flex items-center gap-3 mb-2">
            <span className="w-8 text-xs text-muted-foreground">{b.l}</span>
            <div className="flex-1 bg-white/5 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${b.c}`}
                style={{ width: `${Math.min(100, (b.v / maxMs) * 100)}%` }}
              />
            </div>
            <span className="w-20 text-xs text-right text-slate-300">
              {Math.round(b.v)} ms
            </span>
          </div>
        ))}
      </div>

      {r.performance_summary && (
        <>
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
            <p className="text-sm font-medium text-amber-300">
              {r.performance_summary.status}
            </p>
          </div>
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Bottlenecks
            </p>
            {r.performance_summary.bottlenecks.map((b, i) => (
              <p key={i} className="text-sm flex gap-2 text-slate-300 mb-1">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                {b}
              </p>
            ))}
          </div>
          <div>
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Recommendations
            </p>
            {r.performance_summary.recommendations.slice(0, 5).map((rec, i) => (
              <p key={i} className="text-sm flex gap-2 text-slate-300 mb-1">
                <ChevronRight className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                {rec}
              </p>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function IntrusionPreview({ r }: { r: IntrusionReport }) {
  const sev = r.severity_summary ?? {};
  const priority = r.priority_findings ?? [];

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <StatCard label="Risk Score" value={`${r.risk_score}/10`} />
        <StatCard label="Total Findings" value={r.all_findings?.length ?? 0} />
        <StatCard
          label="Critical + High"
          value={(sev.CRITICAL ?? 0) + (sev.HIGH ?? 0)}
        />
      </div>

      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          Severity Breakdown
        </p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(sev)
            .filter(([, v]) => v > 0)
            .map(([k, v]) => (
              <div key={k} className="flex items-center gap-1.5">
                <SevBadge sev={k} />
                <span className="text-sm font-medium">{v}</span>
              </div>
            ))}
        </div>
      </div>

      {priority.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Priority Findings
          </p>
          <div className="space-y-2">
            {priority.map((f, i) => (
              <div
                key={f.id ?? i}
                className="bg-white/5 border border-white/10 rounded-lg p-3 flex gap-3"
              >
                <SevBadge sev={f.severity} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {f.title}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {f.module}
                    {f.cvss_score ? ` · CVSS ${f.cvss_score}` : ""}
                    {f.cve_id ? ` · ${f.cve_id}` : ""}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          Modules Run
        </p>
        <div className="flex flex-wrap gap-2">
          {(r.modules_run ?? []).map((m) => (
            <span
              key={m}
              className="text-xs bg-white/5 border border-white/10 rounded px-2 py-1 text-slate-300"
            >
              {m.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        Target: <span className="text-white font-mono">{r.target_url}</span>
        {r.completed_at
          ? ` · Completed ${new Date(r.completed_at).toLocaleString()}`
          : ""}
      </p>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────────────────────────────────────

export default function ReportsPage() {
  const [module, setModule] = useState<ModuleType>("vulnerability");
  const [scans, setScans] = useState<ScanItem[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loadingScans, setLoadingScans] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [scansLoaded, setScansLoaded] = useState<ModuleType | null>(null);

  const [vulnReport, setVulnReport] = useState<VulnReport | null>(null);
  const [perfReport, setPerfReport] = useState<PerfReport | null>(null);
  const [intrusionReport, setIntrusionReport] =
    useState<IntrusionReport | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const fetchScans = useCallback(async (m: ModuleType) => {
    setLoadingScans(true);
    setError(null);
    setScans([]);
    try {
      const items = await loadScans(m);
      setScans(items);
      setScansLoaded(m);
    } catch (e: unknown) {
      setError((e as Error).message ?? "Failed to load scans");
    } finally {
      setLoadingScans(false);
    }
  }, []);

  const switchModule = (m: ModuleType) => {
    setModule(m);
    setScansLoaded(null);
    setScans([]);
    setSelectedId("");
    setVulnReport(null);
    setPerfReport(null);
    setIntrusionReport(null);
    setShowPreview(false);
    setError(null);
    fetchScans(m);
  };

  const generate = async () => {
    if (!selectedId) return;
    setLoadingReport(true);
    setError(null);
    setVulnReport(null);
    setPerfReport(null);
    setIntrusionReport(null);
    try {
      const data = await loadReport(module, selectedId);
      if (module === "vulnerability") setVulnReport(data);
      else if (module === "performance") setPerfReport(data);
      else setIntrusionReport(data);
      setShowPreview(true);
    } catch (e: unknown) {
      setError((e as Error).message ?? "Failed to generate report");
    } finally {
      setLoadingReport(false);
    }
  };

  const downloadPDF = () => {
    if (module === "vulnerability" && vulnReport)
      openPDF(buildVulnPDF(vulnReport), `Vulnerability-${vulnReport.run_id}`);
    else if (module === "performance" && perfReport)
      openPDF(buildPerfPDF(perfReport), `Performance-${perfReport.run_id}`);
    else if (module === "intrusion" && intrusionReport)
      openPDF(
        buildIntrusionPDF(intrusionReport),
        `Intrusion-${intrusionReport.scan_id}`,
      );
  };

  const hasReport = vulnReport || perfReport || intrusionReport;
  const cfg = MODULE_CFG[module];
  const Icon = cfg.icon;

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="absolute inset-0 z-0">
        <FlickeringGrid
          className="w-full h-full"
          squareSize={4}
          gridGap={6}
          flickerChance={0.04}
          color="rgb(99,102,241)"
          maxOpacity={0.5}
        />
      </div>

      <div className="relative z-10 p-6 lg:p-10 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold gradient-text">
            CognitoForge
          </Link>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <BarChart2 className="h-4 w-4" /> Security Reports
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="text-center mb-4">
            <h1 className="text-3xl font-bold mb-2">
              Security <span className="gradient-text">Reports</span>
            </h1>
            <p className="text-muted-foreground text-sm">
              Select a scan type, pick a scan, preview and download as PDF
            </p>
          </div>

          {/* Module tabs */}
          <div className="grid grid-cols-3 gap-3">
            {(
              Object.entries(MODULE_CFG) as [
                ModuleType,
                (typeof MODULE_CFG)[ModuleType],
              ][]
            ).map(([key, val]) => {
              const TabIcon = val.icon;
              const active = module === key;
              return (
                <button
                  key={key}
                  onClick={() => switchModule(key)}
                  className={`relative rounded-xl border p-4 text-left transition-all duration-200 ${
                    active
                      ? `bg-gradient-to-br ${val.grad} border-white/20 shadow-lg`
                      : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                  }`}
                >
                  <TabIcon
                    className={`h-5 w-5 mb-2 ${active ? val.accent : "text-muted-foreground"}`}
                  />
                  <p
                    className={`text-sm font-semibold ${active ? "text-white" : "text-muted-foreground"}`}
                  >
                    {val.label}
                  </p>
                  <p
                    className={`text-xs mt-0.5 ${active ? "text-white/60" : "text-muted-foreground/60"}`}
                  >
                    {val.subtitle}
                  </p>
                  {active && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 rounded-xl ring-2 ring-white/20"
                    />
                  )}
                </button>
              );
            })}
          </div>

          {/* Main panel */}
          <div className="glass rounded-xl border border-white/10 p-6 space-y-5">
            {/* Scan selector */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium">Select Scan</label>
                <button
                  onClick={() => {
                    setScansLoaded(null);
                    fetchScans(module);
                  }}
                  className="text-xs text-muted-foreground hover:text-white flex items-center gap-1 transition-colors"
                >
                  <RefreshCw className="h-3 w-3" /> Refresh
                </button>
              </div>

              {loadingScans ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground py-3">
                  <Loader2 className="h-4 w-4 animate-spin" /> Loading scans…
                </div>
              ) : scans.length === 0 ? (
                <div className="text-sm text-muted-foreground py-3 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  {error ??
                    (scansLoaded === module
                      ? "No scans found."
                      : "Click refresh to load scans.")}
                </div>
              ) : (
                <select
                  value={selectedId}
                  onChange={(e) => {
                    setSelectedId(e.target.value);
                    setShowPreview(false);
                    setVulnReport(null);
                    setPerfReport(null);
                    setIntrusionReport(null);
                  }}
                  className="w-full px-4 py-3 bg-background/60 border border-border rounded-lg text-sm"
                >
                  <option value="">— Choose a scan —</option>
                  {scans.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                      {s.meta ? ` (${s.meta})` : ""}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {error && !loadingScans && (
              <div className="flex items-center gap-2 text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
                <XCircle className="h-4 w-4 shrink-0" />
                {error}
              </div>
            )}

            <Button
              variant="purple"
              className="w-full"
              onClick={generate}
              disabled={!selectedId || loadingReport}
            >
              {loadingReport ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Eye className="mr-2 h-4 w-4" />
                  Generate Report
                </>
              )}
            </Button>

            {/* Preview */}
            <AnimatePresence>
              {showPreview && hasReport && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="rounded-xl border border-white/10 bg-white/5 overflow-hidden"
                >
                  <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/5">
                    <div className="flex items-center gap-2">
                      <Icon className={`h-4 w-4 ${cfg.accent}`} />
                      <span className="text-sm font-medium">
                        {cfg.label} Report
                      </span>
                    </div>
                    <button
                      onClick={() => setShowPreview(false)}
                      className="text-muted-foreground hover:text-white"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="p-5">
                    {module === "vulnerability" && vulnReport && (
                      <VulnPreview r={vulnReport} />
                    )}
                    {module === "performance" && perfReport && (
                      <PerfPreview r={perfReport} />
                    )}
                    {module === "intrusion" && intrusionReport && (
                      <IntrusionPreview r={intrusionReport} />
                    )}
                  </div>

                  <div className="px-5 pb-5">
                    <Button
                      variant="purple"
                      className="w-full"
                      onClick={downloadPDF}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download as PDF
                    </Button>
                    <p className="text-xs text-muted-foreground text-center mt-2">
                      Opens a print dialog — select "Save as PDF" in your
                      browser
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
