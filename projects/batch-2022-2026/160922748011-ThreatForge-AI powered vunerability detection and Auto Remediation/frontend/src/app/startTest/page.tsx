"use client";

import Link from "next/link";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Loader2,
  Zap,
  CheckCircle2,
  XCircle,
  Clock,
  Users,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  ToggleLeft,
  ToggleRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

// ─── Types ────────────────────────────────────────────────────────────────────

interface TestConfig {
  targetUrl: string;
  testType: string;
  vus: number;
  duration: string;
  rampUp: string;
  useDefaults: boolean;
}

interface TestResult {
  run_id: string;
  target_url: string;
  test_type: string;
  duration: string;
  vus_max: number;
  vus_avg: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  success_rate: number;
  failure_rate: number;
  avg_response_time: number;
  min_response_time: number;
  max_response_time: number;
  p50_response_time: number;
  p95_response_time: number;
  p99_response_time: number;
  created_at: string;
}

// ─── Recommended defaults per test type ──────────────────────────────────────

const DEFAULTS: Record<
  string,
  { vus: number; duration: string; rampUp: string }
> = {
  load: { vus: 1000, duration: "2m", rampUp: "30s" },
  stress: { vus: 1000, duration: "2m", rampUp: "5s" },
  spike: { vus: 1000, duration: "2m", rampUp: "2s" },
  capacity: { vus: 1000, duration: "30m", rampUp: "1s" },
  quick: { vus: 100, duration: "30s", rampUp: "5s" },
};

const TEST_LABELS: Record<string, string> = {
  load: "Load Test",
  stress: "Stress Test",
  spike: "Spike Test",
  capacity: "Capacity Test",
  quick: "Quick Test",
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmtMs(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
  return `${ms.toFixed(1)}ms`;
}

function fmtNum(n: number): string {
  return n.toLocaleString();
}

function extractPath(url: string): string {
  try {
    return new URL(url).pathname || "/";
  } catch {
    return "/";
  }
}

// ─── Metric Card ─────────────────────────────────────────────────────────────

function MetricCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: "green" | "red" | "blue" | "yellow" | "default";
}) {
  const accentClass: Record<string, string> = {
    green: "text-emerald-400",
    red: "text-red-400",
    blue: "text-blue-400",
    yellow: "text-yellow-400",
    default: "text-foreground",
  };

  return (
    <div className="glass rounded-xl p-4 border border-border/40 flex flex-col gap-1">
      <span className="text-xs text-muted-foreground uppercase tracking-wider">
        {label}
      </span>
      <span className={`text-xl font-bold ${accentClass[accent ?? "default"]}`}>
        {value}
      </span>
      {sub && <span className="text-xs text-muted-foreground">{sub}</span>}
    </div>
  );
}

// ─── Section Header ──────────────────────────────────────────────────────────

function SectionHeader({
  icon: Icon,
  title,
}: {
  icon: React.ElementType;
  title: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <Icon className="h-4 w-4 text-primary" />
      <span className="text-sm font-semibold text-foreground/80 uppercase tracking-wider">
        {title}
      </span>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function StartTestPage() {
  const [config, setConfig] = useState<TestConfig>({
    targetUrl: "",
    testType: "load",
    vus: DEFAULTS.load.vus,
    duration: DEFAULTS.load.duration,
    rampUp: DEFAULTS.load.rampUp,
    useDefaults: true,
  });

  const [phase, setPhase] = useState<"idle" | "running" | "done" | "error">(
    "idle",
  );
  const [statusMsg, setStatusMsg] = useState("");
  const [result, setResult] = useState<TestResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  // ── handlers ────────────────────────────────────────────────────────────────

  function setField<K extends keyof TestConfig>(key: K, val: TestConfig[K]) {
    setConfig((prev) => ({ ...prev, [key]: val }));
  }

  function onTestTypeChange(type: string) {
    const d = DEFAULTS[type];
    setConfig((prev) => ({
      ...prev,
      testType: type,
      ...(prev.useDefaults
        ? { vus: d.vus, duration: d.duration, rampUp: d.rampUp }
        : {}),
    }));
  }

  function onToggleDefaults() {
    const next = !config.useDefaults;
    const d = DEFAULTS[config.testType];
    setConfig((prev) => ({
      ...prev,
      useDefaults: next,
      ...(next ? { vus: d.vus, duration: d.duration, rampUp: d.rampUp } : {}),
    }));
  }

  // ── run test ─────────────────────────────────────────────────────────────────

  async function handleStartTest() {
    if (!config.targetUrl.trim()) {
      setErrorMsg("Please enter a target URL.");
      return;
    }
    setErrorMsg("");
    setPhase("running");
    setResult(null);

    try {
      let testId: string;

      // STEP 1 — start test
      if (config.testType === "quick") {
        setStatusMsg("Running quick performance test…");
        const res = await fetch(
          `http://localhost:8000/api/performance/test/quick?target_url=${encodeURIComponent(config.targetUrl)}`,
          { method: "POST" },
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        testId = data.test_id;
      } else {
        setStatusMsg(`Starting ${TEST_LABELS[config.testType]}…`);
        const path = extractPath(config.targetUrl);
        const body = {
          target_url: config.targetUrl,
          test_type: config.testType,
          vus: config.vus,
          duration: config.duration,
          ramp_up: config.rampUp,
          endpoints: [{ method: "GET", path }],
        };
        const res = await fetch("http://localhost:8000/api/performance/test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        testId = data.test_id;
      }

      // STEP 2 — fetch detailed metrics
      setStatusMsg("Fetching detailed metrics from database…");
      const dbRes = await fetch(
        `http://localhost:8000/api/performance/db/run/${testId}`,
      );
      if (!dbRes.ok) throw new Error(`DB fetch failed: HTTP ${dbRes.status}`);
      const metrics: TestResult = await dbRes.json();

      setResult(metrics);
      setPhase("done");
      setStatusMsg("");
    } catch (err: unknown) {
      setPhase("error");
      setErrorMsg(
        err instanceof Error ? err.message : "Unknown error occurred.",
      );
    }
  }

  // ── render ───────────────────────────────────────────────────────────────────

  return (
    <div className="relative min-h-screen overflow-hidden p-10">
      {/* ── Background (unchanged) ─────────────────────────────────────────── */}
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

      {/* ── Page Content ───────────────────────────────────────────────────── */}
      <div className="relative z-10">
        {/* Brand */}
        <div className="mb-10">
          <Link href="/" className="text-xl font-bold gradient-text">
            CognitoForge
          </Link>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">
              Load / <span className="gradient-text">Performance Testing</span>
            </h1>
            <p className="text-muted-foreground">
              Configure your test, hit Start, and get live metrics from the
              backend.
            </p>
          </div>

          {/* ── Config Form ──────────────────────────────────────────────────── */}
          <div className="glass p-8 rounded-lg border border-border/40 space-y-6 mb-8">
            {/* Target URL */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Target URL
              </label>
              <input
                type="url"
                value={config.targetUrl}
                onChange={(e) => setField("targetUrl", e.target.value)}
                placeholder="https://example.com/login"
                disabled={phase === "running"}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors text-sm"
              />
            </div>

            {/* Test Type */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Test Type
              </label>
              <div className="relative">
                <select
                  value={config.testType}
                  onChange={(e) => onTestTypeChange(e.target.value)}
                  disabled={phase === "running"}
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors text-sm appearance-none pr-10"
                >
                  {Object.entries(TEST_LABELS).map(([val, label]) => (
                    <option key={val} value={val}>
                      {label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
              </div>
            </div>

            {/* Use Recommended Defaults toggle */}
            <div className="flex items-center justify-between py-2 px-4 bg-primary/5 border border-primary/20 rounded-lg">
              <div>
                <p className="text-sm font-medium">Use Recommended Defaults</p>
                <p className="text-xs text-muted-foreground">
                  Auto-fill VUs, duration, and ramp-up for selected test type
                </p>
              </div>
              <button
                onClick={onToggleDefaults}
                disabled={phase === "running"}
                className="flex items-center gap-2 text-primary transition-colors hover:opacity-80"
              >
                {config.useDefaults ? (
                  <ToggleRight className="h-7 w-7 text-primary" />
                ) : (
                  <ToggleLeft className="h-7 w-7 text-muted-foreground" />
                )}
              </button>
            </div>

            {/* Advanced config (hidden for quick test) */}
            {config.testType !== "quick" && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium mb-1 text-muted-foreground uppercase tracking-wider">
                    Virtual Users (VUs)
                  </label>
                  <input
                    type="number"
                    min={1}
                    value={config.vus}
                    onChange={(e) => setField("vus", Number(e.target.value))}
                    disabled={config.useDefaults || phase === "running"}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1 text-muted-foreground uppercase tracking-wider">
                    Duration
                  </label>
                  <input
                    type="text"
                    value={config.duration}
                    onChange={(e) => setField("duration", e.target.value)}
                    disabled={config.useDefaults || phase === "running"}
                    placeholder="e.g. 2m"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1 text-muted-foreground uppercase tracking-wider">
                    Ramp-Up Time
                  </label>
                  <input
                    type="text"
                    value={config.rampUp}
                    onChange={(e) => setField("rampUp", e.target.value)}
                    disabled={config.useDefaults || phase === "running"}
                    placeholder="e.g. 30s"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {errorMsg && (
              <div className="flex items-center gap-2 bg-red-900/20 border border-red-700/40 text-red-300 px-4 py-3 rounded-lg text-sm">
                <XCircle className="h-4 w-4 flex-shrink-0" />
                {errorMsg}
              </div>
            )}

            {/* Start Button */}
            <Button
              variant="purple"
              size="lg"
              className="w-full"
              onClick={handleStartTest}
              disabled={phase === "running"}
            >
              {phase === "running" ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Running Test…
                </>
              ) : (
                <>
                  <Activity className="mr-2 h-4 w-4" />
                  Start {TEST_LABELS[config.testType]}
                </>
              )}
            </Button>
          </div>

          {/* ── Loading / Progress ───────────────────────────────────────────── */}
          <AnimatePresence>
            {phase === "running" && (
              <motion.div
                key="loading"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="glass p-6 rounded-lg border border-blue-500/30 mb-8 flex flex-col items-center gap-4"
              >
                <div className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
                  <span className="text-sm text-blue-300 font-medium">
                    {statusMsg}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-border/40 rounded-full h-1.5 overflow-hidden">
                  <motion.div
                    className="h-full bg-blue-500 rounded-full"
                    initial={{ width: "5%" }}
                    animate={{ width: "90%" }}
                    transition={{ duration: 10, ease: "easeInOut" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Performance tests can take a few minutes — please wait.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Results ──────────────────────────────────────────────────────── */}
          <AnimatePresence>
            {phase === "done" && result && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Success banner */}
                <div className="flex items-center gap-3 bg-emerald-900/20 border border-emerald-700/40 text-emerald-300 px-5 py-3 rounded-lg text-sm">
                  <CheckCircle2 className="h-5 w-5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold">
                      Test completed successfully
                    </span>
                    <span className="text-emerald-400/70 ml-2 text-xs">
                      {TEST_LABELS[result.test_type]} · {result.duration} ·{" "}
                      {result.target_url}
                    </span>
                  </div>
                </div>

                {/* ── Performance Summary ──────────────────────────────────── */}
                <div className="glass p-6 rounded-lg border border-border/40">
                  <SectionHeader
                    icon={TrendingUp}
                    title="Performance Summary"
                  />
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <MetricCard
                      label="Total Requests"
                      value={fmtNum(result.total_requests)}
                      accent="blue"
                    />
                    <MetricCard
                      label="Successful"
                      value={fmtNum(result.successful_requests)}
                      accent="green"
                    />
                    <MetricCard
                      label="Failed"
                      value={fmtNum(result.failed_requests)}
                      accent={result.failed_requests > 0 ? "red" : "default"}
                    />
                    <MetricCard
                      label="Success Rate"
                      value={`${result.success_rate.toFixed(2)}%`}
                      accent={
                        result.success_rate >= 99
                          ? "green"
                          : result.success_rate >= 95
                            ? "yellow"
                            : "red"
                      }
                    />
                    <MetricCard
                      label="Failure Rate"
                      value={`${result.failure_rate.toFixed(2)}%`}
                      accent={
                        result.failure_rate < 1
                          ? "green"
                          : result.failure_rate < 5
                            ? "yellow"
                            : "red"
                      }
                    />
                  </div>
                </div>

                {/* ── Response Times ───────────────────────────────────────── */}
                <div className="glass p-6 rounded-lg border border-border/40">
                  <SectionHeader icon={Clock} title="Response Times" />
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <MetricCard
                      label="Avg Response"
                      value={fmtMs(result.avg_response_time)}
                      accent="blue"
                    />
                    <MetricCard
                      label="P50 (Median)"
                      value={fmtMs(result.p50_response_time)}
                    />
                    <MetricCard
                      label="P95"
                      value={fmtMs(result.p95_response_time)}
                      accent={
                        result.p95_response_time > 5000 ? "yellow" : "default"
                      }
                    />
                    <MetricCard
                      label="P99"
                      value={fmtMs(result.p99_response_time)}
                      accent={
                        result.p99_response_time > 10000 ? "red" : "default"
                      }
                    />
                    <MetricCard
                      label="Min"
                      value={fmtMs(result.min_response_time)}
                      accent="green"
                    />
                    <MetricCard
                      label="Max"
                      value={fmtMs(result.max_response_time)}
                      accent={
                        result.max_response_time > 30000 ? "red" : "yellow"
                      }
                    />
                  </div>
                </div>

                {/* ── Traffic ──────────────────────────────────────────────── */}
                <div className="glass p-6 rounded-lg border border-border/40">
                  <SectionHeader icon={Users} title="Traffic" />
                  <div className="grid grid-cols-2 gap-3">
                    <MetricCard
                      label="Max VUs"
                      value={fmtNum(result.vus_max)}
                      accent="blue"
                    />
                    <MetricCard
                      label="Average VUs"
                      value={result.vus_avg.toFixed(1)}
                    />
                  </div>
                </div>

                {/* Run again */}
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setPhase("idle");
                    setResult(null);
                  }}
                >
                  <Zap className="mr-2 h-4 w-4" />
                  Run Another Test
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Error state ──────────────────────────────────────────────────── */}
          <AnimatePresence>
            {phase === "error" && (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass p-6 rounded-lg border border-red-700/40"
              >
                <div className="flex items-start gap-3 text-red-300 mb-4">
                  <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-sm">Test failed</p>
                    <p className="text-xs text-red-400/70 mt-1">{errorMsg}</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setPhase("idle");
                    setErrorMsg("");
                  }}
                >
                  Try Again
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
