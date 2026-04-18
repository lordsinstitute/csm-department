"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  GitBranch,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Activity,
  FileText,
  Sparkles,
  RefreshCw,
  BarChart3,
  Target,
  Zap,
  Database,
  Server,
  Cloud,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import Link from "next/link";
import {
  getGradientStatus,
  type GradientStatus,
  type SnowflakeSeveritySummary,
} from "@/lib/api";

interface DashboardStats {
  totalRepositories: number;
  totalSimulations: number;
  totalVulnerabilities: number;
  criticalVulnerabilities: number;
  highVulnerabilities: number;
  mediumVulnerabilities: number;
  lowVulnerabilities: number;
  averageRiskScore: number;
  lastSimulation: string | null;
  aiPoweredScans: number;
  fallbackScans: number;
}

interface RecentSimulation {
  repo_id: string;
  run_id: string;
  timestamp: string;
  overall_severity: string;
  total_steps: number;
  plan_source: "gemini" | "fallback" | "legacy";
  ai_insight?: string;
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentSimulations, setRecentSimulations] = useState<
    RecentSimulation[]
  >([]);
  const [snowflakeSummary, setSnowflakeSummary] =
    useState<SnowflakeSeveritySummary | null>(null);
  const [gradientStatus, setGradientStatus] = useState<GradientStatus | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const { showSuccess, showError } = useToast();

  const fetchDashboardData = async () => {
    try {
      setIsRefreshing(true);

      // Fetch all dashboard KPIs and recent simulations in parallel from DB
      const API_BASE =
        process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

      const [metricsRes, recentsRes, gradientRes] = await Promise.all([
        fetch(`${API_BASE}/api/dashboard/metrics`),
        fetch(`${API_BASE}/api/dashboard/recent-simulations?limit=5`),
        getGradientStatus(),
      ]);

      if (!metricsRes.ok || !recentsRes.ok) {
        throw new Error("Failed to fetch dashboard data from database");
      }

      const metricsJson = await metricsRes.json();
      const recentsJson = await recentsRes.json();

      if (!metricsJson.success || !recentsJson.success) {
        throw new Error("API returned an error response");
      }

      const m = metricsJson.data;
      const dist = m.vulnerability_distribution ?? {};

      setStats({
        totalRepositories: m.repos_analyzed ?? 0,
        totalSimulations: m.total_scans ?? 0,
        totalVulnerabilities: m.total_vulnerabilities ?? 0,
        criticalVulnerabilities: dist.critical ?? 0,
        highVulnerabilities: dist.high ?? 0,
        mediumVulnerabilities: dist.medium ?? 0,
        lowVulnerabilities: dist.low ?? 0,
        averageRiskScore: m.avg_risk_score ?? 0,
        lastSimulation: m.last_scan ?? null,
        aiPoweredScans: m.gemini_scans ?? 0,
        fallbackScans: m.fallback_scans ?? 0,
      });

      // Recent simulations are already shaped correctly by the backend
      setRecentSimulations(recentsJson.data ?? []);

      // Gradient status (unchanged)
      if (gradientRes.success && gradientRes.data) {
        setGradientStatus(gradientRes.data.status);
      }

      if (!isLoading) {
        showSuccess("Dashboard Updated", "Data refreshed successfully");
      }
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      showError(
        "Failed to Load",
        "Could not fetch dashboard data. Using demo mode.",
      );

      setStats({
        totalRepositories: 0,
        totalSimulations: 0,
        totalVulnerabilities: 0,
        criticalVulnerabilities: 0,
        highVulnerabilities: 0,
        mediumVulnerabilities: 0,
        lowVulnerabilities: 0,
        averageRiskScore: 0,
        lastSimulation: null,
        aiPoweredScans: 0,
        fallbackScans: 0,
      });
      setRecentSimulations([]);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const getTimeAgo = (timestamp: string | null) => {
    if (!timestamp) return "Never";

    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "text-red-500 bg-red-500/10 border-red-500/20";
      case "high":
        return "text-orange-500 bg-orange-500/10 border-orange-500/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "low":
        return "text-blue-500 bg-blue-500/10 border-blue-500/20";
      default:
        return "text-gray-500 bg-gray-500/10 border-gray-500/20";
    }
  };

  const getSourceBadge = (source: string) => {
    switch (source) {
      case "gemini":
        return {
          icon: "🤖",
          label: "AI-Powered",
          color: "text-green-500 bg-green-500/10",
        };
      case "fallback":
        return {
          icon: "⚙️",
          label: "Deterministic",
          color: "text-yellow-500 bg-yellow-500/10",
        };
      default:
        return {
          icon: "❓",
          label: "Legacy",
          color: "text-gray-500 bg-gray-500/10",
        };
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Security <span className="gradient-text">Dashboard</span>
          </h1>
          <p className="text-muted-foreground">
            Real-time analytics powered by Gemini AI
          </p>
        </div>
        <Button
          onClick={fetchDashboardData}
          disabled={isRefreshing}
          variant="outline"
          className="flex items-center gap-2"
        >
          <RefreshCw
            className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Repositories */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-6 rounded-lg border border-border/40"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <GitBranch className="h-6 w-6 text-blue-500" />
            </div>
            <span className="text-2xl font-bold">
              {stats?.totalRepositories || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">
            Repositories Analyzed
          </h3>
        </motion.div>

        {/* Total Simulations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass p-6 rounded-lg border border-border/40"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Activity className="h-6 w-6 text-purple-500" />
            </div>
            <span className="text-2xl font-bold">
              {stats?.totalSimulations || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">
            Total Scans
          </h3>
        </motion.div>

        {/* Total Vulnerabilities */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass p-6 rounded-lg border border-border/40"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-500" />
            </div>
            <span className="text-2xl font-bold">
              {stats?.totalVulnerabilities || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">
            Total Vulnerabilities
          </h3>
        </motion.div>

        {/* Average Risk Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass p-6 rounded-lg border border-border/40"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-500/10 rounded-lg">
              <TrendingUp className="h-6 w-6 text-orange-500" />
            </div>
            <span className="text-2xl font-bold">
              {stats?.averageRiskScore || 0}/10
            </span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">
            Avg Risk Score
          </h3>
        </motion.div>
      </div>

      {/* Vulnerability Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Vulnerability Distribution */}
        <div className="glass p-6 rounded-lg border border-border/40">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Vulnerability Distribution
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-sm">Critical</span>
              </div>
              <span className="text-sm font-medium">
                {stats?.criticalVulnerabilities || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                <span className="text-sm">High</span>
              </div>
              <span className="text-sm font-medium">
                {stats?.highVulnerabilities || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="text-sm">Medium</span>
              </div>
              <span className="text-sm font-medium">
                {stats?.mediumVulnerabilities || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="text-sm">Low</span>
              </div>
              <span className="text-sm font-medium">
                {stats?.lowVulnerabilities || 0}
              </span>
            </div>
          </div>
        </div>

        {/* AI Analysis Stats */}
        <div className="glass p-6 rounded-lg border border-border/40">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            AI-Powered Analysis
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-500/5 rounded-lg border border-green-500/20">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🤖</span>
                <span className="text-sm font-medium">Gemini AI Scans</span>
              </div>
              <span className="text-lg font-bold text-green-500">
                {stats?.aiPoweredScans || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-500/5 rounded-lg border border-yellow-500/20">
              <div className="flex items-center gap-2">
                <span className="text-2xl">⚙️</span>
                <span className="text-sm font-medium">Fallback Scans</span>
              </div>
              <span className="text-lg font-bold text-yellow-500">
                {stats?.fallbackScans || 0}
              </span>
            </div>
            <div className="pt-2 border-t border-border/40">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last Scan</span>
                <span className="font-medium">
                  {getTimeAgo(stats?.lastSimulation || null)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Snowflake & Gradient Status Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Snowflake Analytics */}
        {/* <div className="glass p-6 rounded-lg border border-blue-500/20">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Database className="h-5 w-5 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold">Snowflake Analytics</h3>
          </div>
          
          {snowflakeSummary ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Critical Threats</span>
                <span className="text-lg font-bold text-red-500">{snowflakeSummary.critical}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">High Severity</span>
                <span className="text-lg font-bold text-orange-500">{snowflakeSummary.high}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Medium Risk</span>
                <span className="text-lg font-bold text-yellow-500">{snowflakeSummary.medium}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Low Risk</span>
                <span className="text-lg font-bold text-blue-500">{snowflakeSummary.low}</span>
              </div>
              <div className="pt-3 border-t border-border/40">
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <CheckCircle className="h-3 w-3 text-green-500" />
                  Data synced from Snowflake warehouse
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Server className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Snowflake data unavailable</p>
              <p className="text-xs mt-1">Configure credentials to enable analytics</p>
            </div>
          )}
        </div>
        */}

        {/* Gradient Status */}
        <div className="glass p-6 rounded-lg border border-purple-500/20">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-500/10 rounded-lg">
              <Cloud className="h-5 w-5 text-purple-500" />
            </div>
            <h3 className="text-lg font-semibold">Gradient Cluster</h3>
          </div>

          {gradientStatus ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <span
                  className={`flex items-center gap-2 ${gradientStatus.connected ? "text-green-500" : "text-red-500"}`}
                >
                  <div
                    className={`h-2 w-2 rounded-full ${gradientStatus.connected ? "bg-green-500" : "bg-red-500"} animate-pulse`}
                  ></div>
                  {gradientStatus.connected ? "Connected" : "Disconnected"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Mode</span>
                <span
                  className={`px-2 py-1 rounded text-xs ${gradientStatus.mock_mode ? "bg-yellow-500/10 text-yellow-500" : "bg-green-500/10 text-green-500"}`}
                >
                  {gradientStatus.mock_mode ? "Simulated" : "Production"}
                </span>
              </div>
              <div className="pt-3 border-t border-border/40">
                <p className="text-xs text-muted-foreground">
                  {gradientStatus.message}
                </p>
              </div>
              {gradientStatus.mock_mode && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
                  <p className="text-xs text-yellow-600 dark:text-yellow-400 flex items-center gap-2">
                    <Sparkles className="h-3 w-3" />
                    Running in mock mode for development
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Cloud className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Gradient status unavailable</p>
              <p className="text-xs mt-1">Check service configuration</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Simulations */}
      <div className="glass p-6 rounded-lg border border-border/40">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            Recent Simulations
          </h3>
          <Link href="/demo">
            <Button variant="outline" size="sm">
              Run New Scan
            </Button>
          </Link>
        </div>

        {recentSimulations.length > 0 ? (
          <div className="space-y-3">
            {recentSimulations.map((sim, index) => {
              const sourceBadge = getSourceBadge(sim.plan_source);
              return (
                <motion.div
                  key={sim.run_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border border-border/40 rounded-lg hover:border-primary/40 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{sim.repo_id}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-xs border ${getSeverityColor(sim.overall_severity)}`}
                        >
                          {sim.overall_severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        <span>{sim.total_steps} attack vectors</span>
                        <span>•</span>
                        <span>{getTimeAgo(sim.timestamp)}</span>
                      </div>
                    </div>
                    <div
                      className={`px-2 py-1 rounded-lg text-xs flex items-center gap-1 ${sourceBadge.color}`}
                    >
                      <span>{sourceBadge.icon}</span>
                      <span>{sourceBadge.label}</span>
                    </div>
                  </div>
                  {sim.ai_insight && (
                    <p className="text-sm text-muted-foreground mt-2 pl-6">
                      {sim.ai_insight.substring(0, 100)}...
                    </p>
                  )}
                </motion.div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="mb-4">No simulations yet</p>
            <Link href="/demo">
              <Button>
                <Zap className="mr-2 h-4 w-4" />
                Run First Scan
              </Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
