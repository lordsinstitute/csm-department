"use client";

import Link from "next/link";
import { useState } from "react";
import {
  Loader2,
  Database,
  SendHorizonal,
  Globe,
  FolderOpen,
  CheckCircle,
  ChevronRight,
  FileCode2,
  RefreshCw,
  CornerDownLeft,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";

const BASE_URL = "http://localhost:8000";

type Mode = "select" | "url" | "indexed";

interface Project {
  repo_id: string;
  indexed: boolean;
}

interface AskResponse {
  answer: string;
  sources: string[];
  status: string;
  retrieved_chunks: number;
  top_matches: { name: string; type: string; score: number; reason: string }[];
}

export default function AssistPage() {
  // ── Mode selection ──────────────────────────────────────────────────
  const [mode, setMode] = useState<Mode>("select");

  // ── URL workflow ────────────────────────────────────────────────────
  const [repoUrl, setRepoUrl] = useState("");
  const [repoId, setRepoId] = useState("");        // derived after step-1
  const [urlStep, setUrlStep] = useState<"idle" | "uploading" | "indexing" | "ready">("idle");
  const [uploadInfo, setUploadInfo] = useState<{ files_indexed: number; high_risk_files: number } | null>(null);

  // ── Indexed projects workflow ───────────────────────────────────────
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // ── Shared Q&A ──────────────────────────────────────────────────────
  const [question, setQuestion] = useState("");
  const [askLoading, setAskLoading] = useState(false);
  const [askResponse, setAskResponse] = useState<AskResponse | null>(null);

  // ── Error ───────────────────────────────────────────────────────────
  const [error, setError] = useState("");

  // ── Helpers ─────────────────────────────────────────────────────────
  const activeRepoId = mode === "url" ? repoId : selectedProject?.repo_id ?? "";
  const isReady =
    (mode === "url" && urlStep === "ready") ||
    (mode === "indexed" && selectedProject !== null);

  function reset() {
    setMode("select");
    setRepoUrl("");
    setRepoId("");
    setUrlStep("idle");
    setUploadInfo(null);
    setProjects([]);
    setSelectedProject(null);
    setQuestion("");
    setAskResponse(null);
    setError("");
  }

  // ── URL workflow handlers ───────────────────────────────────────────
  async function handleUploadRepo() {
    setError("");
    if (!repoUrl.trim()) return setError("Please enter a repository URL.");

    // derive repo_id from URL (last path segment)
    const parts = repoUrl.replace(/\/$/, "").split("/");
    const id = parts[parts.length - 1] || "repo";
    setRepoId(id);
    setUrlStep("uploading");

    try {
      const res = await fetch(`${BASE_URL}/upload_repo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_id: id, repo_url: repoUrl }),
      });
      if (!res.ok) throw new Error(`Upload failed (${res.status})`);
      const data = await res.json();
      setUploadInfo({ files_indexed: data.files_indexed, high_risk_files: data.high_risk_files });

      // step 2 — index
      setUrlStep("indexing");
      const idxRes = await fetch(`${BASE_URL}/code-assist/index/${id}`, { method: "POST" });
      if (!idxRes.ok) throw new Error(`Indexing failed (${idxRes.status})`);

      setUrlStep("ready");
    } catch (e: any) {
      setError(e.message || "Something went wrong.");
      setUrlStep("idle");
    }
  }

  // ── Indexed projects handler ────────────────────────────────────────
  async function handleLoadProjects() {
    setError("");
    setProjectsLoading(true);
    setProjects([]);
    try {
      const res = await fetch(`${BASE_URL}/code-assist/projects`);
      if (!res.ok) throw new Error(`Failed to fetch projects (${res.status})`);
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (e: any) {
      setError(e.message || "Could not load projects.");
    } finally {
      setProjectsLoading(false);
    }
  }

  // ── Ask handler ─────────────────────────────────────────────────────
  async function handleAsk() {
    setError("");
    setAskResponse(null);
    if (!question.trim()) return setError("Please enter a question.");

    setAskLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/code-assist/ask/${activeRepoId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Request failed (${res.status})`);
      const data: AskResponse = await res.json();
      setAskResponse(data);
    } catch (e: any) {
      setError(e.message || "Failed to get a response.");
    } finally {
      setAskLoading(false);
    }
  }

  // ── Render ──────────────────────────────────────────────────────────
  return (
    <div className="relative min-h-screen overflow-hidden p-10">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <FlickeringGrid
          className="w-full h-full"
          squareSize={4}
          gridGap={6}
          flickerChance={0.06}
          color="rgb(59, 130, 246)"
          maxOpacity={0.8}
        />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-10 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold gradient-text">
            CognitoForge
          </Link>
          {mode !== "select" && (
            <button
              onClick={reset}
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="h-3.5 w-3.5" />
              Start over
            </button>
          )}
        </div>

        <div className="max-w-2xl mx-auto">
          {/* Card */}
          <div className="glass p-8 rounded-lg">
            <h1 className="text-3xl font-bold mb-2">
              Code <span className="gradient-text">Assist</span>
            </h1>
            <p className="text-muted-foreground mb-8">
              Ask questions about any codebase — from a URL or an already-indexed project.
            </p>

            {/* ── MODE SELECTION ── */}
            {mode === "select" && (
              <div className="grid grid-cols-2 gap-4">
                <ModeCard
                  icon={<Globe className="h-6 w-6 text-blue-400" />}
                  title="New Repository"
                  description="Index a GitHub URL and start asking questions"
                  onClick={() => setMode("url")}
                />
                <ModeCard
                  icon={<FolderOpen className="h-6 w-6 text-purple-400" />}
                  title="Indexed Projects"
                  description="Pick from previously indexed repositories"
                  onClick={() => { setMode("indexed"); handleLoadProjects(); }}
                />
              </div>
            )}

            {/* ── URL WORKFLOW ── */}
            {mode === "url" && !isReady && (
              <div className="space-y-4">
                <label className="block text-sm font-medium">Repository URL</label>
                <input
                  type="url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleUploadRepo()}
                  placeholder="https://github.com/username/repository"
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors"
                  disabled={urlStep !== "idle"}
                />

                {urlStep === "idle" && (
                  <Button variant="purple" size="lg" className="w-full" onClick={handleUploadRepo}>
                    <Database className="mr-2 h-4 w-4" />
                    Load & Index Repository
                  </Button>
                )}

                {urlStep === "uploading" && (
                  <StatusBadge icon={<Loader2 className="h-4 w-4 animate-spin" />} text="Uploading repository…" color="blue" />
                )}

                {urlStep === "indexing" && (
                  <>
                    {uploadInfo && (
                      <div className="flex gap-3">
                        <InfoChip label="Files indexed" value={uploadInfo.files_indexed} />
                        <InfoChip label="High-risk files" value={uploadInfo.high_risk_files} accent />
                      </div>
                    )}
                    <StatusBadge icon={<Loader2 className="h-4 w-4 animate-spin" />} text="Indexing chunks…" color="purple" />
                  </>
                )}
              </div>
            )}

            {/* ── INDEXED PROJECTS WORKFLOW ── */}
            {mode === "indexed" && !isReady && (
              <div className="space-y-3">
                {projectsLoading && (
                  <StatusBadge icon={<Loader2 className="h-4 w-4 animate-spin" />} text="Loading projects…" color="blue" />
                )}
                {!projectsLoading && projects.length === 0 && !error && (
                  <p className="text-muted-foreground text-sm text-center py-4">No indexed projects found.</p>
                )}
                {projects.map((p) => (
                  <button
                    key={p.repo_id}
                    onClick={() => setSelectedProject(p)}
                    className="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-border bg-background/50 hover:border-primary/60 hover:bg-primary/5 transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <FileCode2 className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                      <span className="font-medium text-sm">{p.repo_id}</span>
                      {p.indexed && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                          indexed
                        </span>
                      )}
                    </div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </button>
                ))}
                {!projectsLoading && projects.length > 0 && (
                  <button
                    onClick={handleLoadProjects}
                    className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors mx-auto mt-1"
                  >
                    <RefreshCw className="h-3 w-3" /> Refresh
                  </button>
                )}
              </div>
            )}

            {/* ── READY HEADER (both modes) ── */}
            {isReady && !askResponse && (
              <div className="mb-6 flex items-center gap-3 px-4 py-3 rounded-lg bg-green-500/10 border border-green-500/20">
                <CheckCircle className="h-4 w-4 text-green-400 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-green-300">Ready — <span className="font-mono">{activeRepoId}</span></p>
                  <p className="text-xs text-muted-foreground">Ask anything about this codebase</p>
                </div>
              </div>
            )}

            {/* ── Q&A box ── */}
            {isReady && (
              <div className="space-y-3 mt-2">
                <label className="block text-sm font-medium">Your question</label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && e.ctrlKey) handleAsk(); }}
                  rows={4}
                  placeholder="e.g. Explain the authentication flow of this repo…"
                  className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors resize-none"
                  disabled={askLoading}
                />
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <CornerDownLeft className="h-3 w-3" /> Ctrl+Enter to send
                  </span>
                  <Button variant="purple" onClick={handleAsk} disabled={askLoading}>
                    {askLoading ? (
                      <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Thinking…</>
                    ) : (
                      <><SendHorizonal className="mr-2 h-4 w-4" />Ask</>
                    )}
                  </Button>
                </div>
              </div>
            )}

            {/* ── Error ── */}
            {error && (
              <div className="mt-4 bg-red-900/20 border border-red-700/50 text-red-300 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
          </div>

          {/* ── RESPONSE ── */}
          {askResponse && (
            <div className="mt-6 glass rounded-lg overflow-hidden border border-border/40">
              {/* Answer */}
              <div className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-semibold text-lg">Answer</h2>
                  <div className="flex gap-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {askResponse.retrieved_chunks} chunks
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${
                      askResponse.status === "success"
                        ? "bg-green-500/10 text-green-400 border-green-500/20"
                        : "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
                    }`}>
                      {askResponse.status}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {askResponse.answer}
                </p>
              </div>

              {/* Sources */}
              {askResponse.sources?.length > 0 && (
                <div className="border-t border-border/40 px-6 py-4">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {askResponse.sources.map((s, i) => (
                      <span key={i} className="text-xs px-2.5 py-1 rounded-md bg-background border border-border text-muted-foreground font-mono">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Top matches */}
              {askResponse.top_matches?.length > 0 && (
                <div className="border-t border-border/40 px-6 py-4">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Top Matches</p>
                  <div className="space-y-2">
                    {askResponse.top_matches.map((m, i) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="w-4 h-4 rounded-sm bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px]">
                            {i + 1}
                          </span>
                          <span className="font-mono text-foreground">{m.name}</span>
                          <span className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{m.type}</span>
                        </div>
                        <span className="text-muted-foreground">{m.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ask another */}
              <div className="border-t border-border/40 px-6 py-4">
                <button
                  onClick={() => { setAskResponse(null); setQuestion(""); }}
                  className="text-sm text-primary hover:underline"
                >
                  Ask another question →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────

function ModeCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-start gap-3 p-5 rounded-lg border border-border bg-background/40 hover:border-primary/50 hover:bg-primary/5 transition-all text-left group"
    >
      <div className="p-2.5 rounded-lg bg-muted group-hover:bg-primary/10 transition-colors">
        {icon}
      </div>
      <div>
        <p className="font-semibold text-sm mb-1">{title}</p>
        <p className="text-xs text-muted-foreground leading-snug">{description}</p>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all mt-auto self-end" />
    </button>
  );
}

function StatusBadge({
  icon,
  text,
  color,
}: {
  icon: React.ReactNode;
  text: string;
  color: "blue" | "purple";
}) {
  const cls =
    color === "blue"
      ? "bg-blue-500/10 border-blue-500/20 text-blue-300"
      : "bg-purple-500/10 border-purple-500/20 text-purple-300";
  return (
    <div className={`flex items-center gap-2 px-4 py-3 rounded-lg border text-sm ${cls}`}>
      {icon}
      {text}
    </div>
  );
}

function InfoChip({ label, value, accent }: { label: string; value: number; accent?: boolean }) {
  return (
    <div className={`flex-1 text-center px-3 py-2 rounded-lg border text-sm ${
      accent
        ? "bg-orange-500/10 border-orange-500/20 text-orange-300"
        : "bg-muted border-border text-muted-foreground"
    }`}>
      <span className="font-bold text-lg block">{value}</span>
      <span className="text-xs">{label}</span>
    </div>
  );
}