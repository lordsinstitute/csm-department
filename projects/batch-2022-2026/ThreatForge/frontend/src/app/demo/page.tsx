'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ToastContainer, useToast } from '@/components/ui/toast';
import { LatestReport } from '@/components/reports';
import { uploadRepository, simulateAttack, fetchLatestReport, runCompleteAnalysis, healthCheck } from '@/lib/api';
import { validateRepoUrl, validateAnalysisType, combineValidationResults } from '@/lib/validation';
import { ProtectedRoute, UserProfile } from '@/components/auth';
import { WelcomeDashboard } from '@/components/WelcomeDashboard';
import { useAuth0 } from '@auth0/auth0-react';
import {
  Shield,
  GitBranch,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Download,
  RefreshCw,
  Play,
  Loader2,
  ArrowLeft,
  Code,
  Database,
  Lock,
  Cloud,
  Server
} from 'lucide-react';
import Link from 'next/link';

interface AnalysisStep {
  id: string;
  message: string;
  status: 'pending' | 'running' | 'complete';
  duration: number;
}

interface Vulnerability {
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  cve?: string;
}

function DemoHeader() {
  const { user } = useAuth0();
  
  return (
    <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-xl font-bold gradient-text">
              CognitoForge
            </Link>
            <div className="h-6 w-px bg-border/40" />
            <span className="text-muted-foreground">Security Analysis Demo</span>
          </div>
          
          {user && <UserProfile />}
        </div>
      </div>
    </header>
  );
}

function RepoInputForm({ onSubmit, isLoading }: { 
  onSubmit: (repoUrl: string, analysisType: string) => void; 
  isLoading: boolean;
}) {
  const [repoUrl, setRepoUrl] = useState('');
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [errors, setErrors] = useState<string[]>([]);
  const [touched, setTouched] = useState({ repoUrl: false, analysisType: false });

  const validateForm = () => {
    const repoValidation = validateRepoUrl(repoUrl);
    const analysisValidation = validateAnalysisType(analysisType);
    const combined = combineValidationResults(repoValidation, analysisValidation);
    
    setErrors(combined.errors);
    return combined.isValid;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ repoUrl: true, analysisType: true });
    
    if (validateForm()) {
      onSubmit(repoUrl, analysisType);
    }
  };

  const handleRepoUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRepoUrl(e.target.value);
    if (touched.repoUrl) {
      validateForm();
    }
  };

  const handleAnalysisTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setAnalysisType(e.target.value);
    if (touched.analysisType) {
      validateForm();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">
          AI <span className="gradient-text">Security Analysis</span>
        </h1>
        <p className="text-muted-foreground">
          Enter a repository URL to simulate an AI-powered red team analysis
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 glass p-8 rounded-lg">
        {errors.length > 0 && (
          <div className="bg-red-900/20 border border-red-700/50 text-red-300 px-4 py-3 rounded-lg">
            <ul className="text-sm space-y-1">
              {errors.map((error, index) => (
                <li key={index}>• {error}</li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <label htmlFor="repoUrl" className="block text-sm font-medium mb-2">
            Repository URL
          </label>
          <input
            id="repoUrl"
            type="url"
            value={repoUrl}
            onChange={handleRepoUrlChange}
            onBlur={() => setTouched(prev => ({ ...prev, repoUrl: true }))}
            className={`w-full px-4 py-3 bg-background border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors ${
              touched.repoUrl && errors.some(e => e.includes('Repository URL')) 
                ? 'border-red-500' 
                : 'border-border'
            }`}
            placeholder="https://github.com/username/repository"
            required
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="analysisType" className="block text-sm font-medium mb-2">
            Analysis Type
          </label>
          <select
            id="analysisType"
            value={analysisType}
            onChange={handleAnalysisTypeChange}
            onBlur={() => setTouched(prev => ({ ...prev, analysisType: true }))}
            className={`w-full px-4 py-3 bg-background border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-colors ${
              touched.analysisType && errors.some(e => e.includes('Analysis type')) 
                ? 'border-red-500' 
                : 'border-border'
            }`}
            required
            disabled={isLoading}
          >
            <option value="comprehensive">Comprehensive Security Audit</option>
            <option value="quick">Quick Vulnerability Scan</option>
            <option value="cicd">CI/CD Pipeline Analysis</option>
            <option value="dependencies">Dependency Security Check</option>
          </select>
        </div>

        <Button
          type="submit"
          size="lg"
          className="w-full"
          disabled={isLoading || errors.length > 0}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Initializing Analysis...
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Start Security Analysis
            </>
          )}
        </Button>
      </form>
    </motion.div>
  );
}

function AnalysisProgress({ 
  steps, 
  progress 
}: { 
  steps: AnalysisStep[]; 
  progress: number; 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">
          Analysis <span className="gradient-text">In Progress</span>
        </h1>
        <p className="text-muted-foreground">
          AI is analyzing your repository for security vulnerabilities
        </p>
      </div>

      {/* Progress Bar */}
      <div className="glass p-6 rounded-lg mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Progress</span>
          <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
          <motion.div
            className="h-3 rounded-full"
            style={{ 
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)'
            }}
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          />
        </div>
      </div>

      {/* Analysis Steps */}
      <div className="glass p-6 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Analysis Steps</h3>
        <div className="space-y-3">
          {steps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3 p-3 rounded-lg border border-border/40"
            >
              <div className="flex-shrink-0">
                {step.status === 'complete' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {step.status === 'running' && (
                  <Loader2 className="h-5 w-5 text-primary animate-spin" />
                )}
                {step.status === 'pending' && (
                  <div className="h-5 w-5 rounded-full border-2 border-muted" />
                )}
              </div>
              <span className={`text-sm ${
                step.status === 'complete' ? 'text-foreground' : 'text-muted-foreground'
              }`}>
                {step.message}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function SecurityReport({ 
  onNewAnalysis,
  repoId,
  analysisResult 
}: { 
  onNewAnalysis: () => void;
  repoId?: string | null;
  analysisResult?: any;
}) {
  const [isDownloading, setIsDownloading] = useState(false);
  const { showSuccess, showError } = useToast();
  
  // Only show real data from backend - no fallbacks
  if (!analysisResult) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-2">No Analysis Data</h2>
        <p className="text-muted-foreground mb-6">Run a security analysis to see results</p>
        <Button onClick={onNewAnalysis}>Start New Analysis</Button>
      </div>
    );
  }

  // Debug logging
  console.log('Analysis Result:', analysisResult);
  console.log('Plan:', analysisResult.plan);
  console.log('Steps:', analysisResult.plan?.steps);
  console.log('Gemini Metadata:', analysisResult.gemini_metadata);

  const displayData = analysisResult;

  // Extract real vulnerabilities from Gemini-generated attack plan
  const vulnerabilities: Vulnerability[] = analysisResult.plan?.steps ? 
    analysisResult.plan.steps.map((step: any, index: number) => ({
      title: step.description || `Attack Step ${index + 1}`,
      severity: (step.severity || 'medium').toLowerCase(),
      description: `MITRE ATT&CK: ${step.technique_id || 'N/A'} | Affected Files: ${step.affected_files?.length || 0}`,
      cve: step.technique_id // Use MITRE technique as identifier
    })) : [];

  console.log('Parsed Vulnerabilities:', vulnerabilities);

  // Calculate actual analysis duration if timestamp is available
  const getAnalysisDuration = () => {
    if (analysisResult?.timestamp) {
      const timestamp = new Date(analysisResult.timestamp);
      const now = new Date();
      const diffMs = now.getTime() - timestamp.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffSecs = Math.floor((diffMs % 60000) / 1000);
      
      if (diffMins > 0) {
        return `${diffMins}m ${diffSecs}s`;
      }
      return `${diffSecs}s`;
    }
    return 'N/A';
  };

  // Get AI confidence indicator
  const getAIConfidence = () => {
    const isGemini = analysisResult?.gemini_metadata?.plan_source === 'gemini';
    const model = analysisResult?.gemini_metadata?.model_used;
    
    if (isGemini && model) {
      // Gemini AI is high confidence
      return {
        level: 'High',
        color: 'text-green-500',
        icon: '🤖',
        label: 'AI-Powered',
        details: `Generated by ${model}`
      };
    } else if (analysisResult?.gemini_metadata?.plan_source === 'fallback') {
      return {
        level: 'Medium',
        color: 'text-yellow-500',
        icon: '⚙️',
        label: 'Deterministic',
        details: 'Rule-based analysis'
      };
    }
    return {
      level: 'Unknown',
      color: 'text-gray-500',
      icon: '❓',
      label: 'Standard',
      details: 'Legacy analysis'
    };
  };

  const aiConfidence = getAIConfidence();

  const riskScore = () => {
    const severity = displayData.plan?.overall_severity || 'medium';
    switch (severity.toLowerCase()) {
      case 'critical': return { score: '9.5/10', color: 'text-red-500', level: 'Critical Risk' };
      case 'high': return { score: '8.5/10', color: 'text-orange-500', level: 'High Risk' };
      case 'medium': return { score: '6.0/10', color: 'text-yellow-500', level: 'Medium Risk' };
      case 'low': return { score: '3.0/10', color: 'text-green-500', level: 'Low Risk' };
      default: return { score: '5.0/10', color: 'text-gray-500', level: 'Unknown Risk' };
    }
  };

  const risk = riskScore();
  
  // Calculate total vulnerabilities from actual plan steps
  const totalVulns = vulnerabilities.length;

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    try {
      // In a real app, this would call the API
      // const result = await downloadReport('demo-report-id', 'pdf');
      
      // For demo, simulate download
      await new Promise(resolve => setTimeout(resolve, 2000));
      showSuccess('Download Complete', 'Security report downloaded successfully');
    } catch (error) {
      showError('Download Failed', 'Failed to download report');
    } finally {
      setIsDownloading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      default: return 'text-muted-foreground bg-muted/10 border-muted/20';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto"
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">
          Security <span className="gradient-text">Analysis Report</span>
        </h1>
        <p className="text-muted-foreground">
          Comprehensive security analysis completed successfully
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mb-8">
        {/* Risk Score */}
        <div className="glass p-6 rounded-lg text-center">
          <div className={`text-3xl font-bold mb-2 ${risk.color}`}>{risk.score}</div>
          <div className="text-sm text-muted-foreground">Risk Score</div>
          <div className={`text-sm mt-1 ${risk.color}`}>{risk.level}</div>
        </div>

        {/* Vulnerabilities Found */}
        <div className="glass p-6 rounded-lg text-center">
          <div className="text-3xl font-bold text-orange-500 mb-2">{totalVulns}</div>
          <div className="text-sm text-muted-foreground">Issues Found</div>
          <div className="text-orange-500 text-sm mt-1">Action Required</div>
        </div>

        {/* Analysis Duration & AI Confidence */}
        <div className="glass p-6 rounded-lg text-center">
          <div className="text-3xl font-bold text-primary mb-2">
            {getAnalysisDuration()}
          </div>
          <div className="text-sm text-muted-foreground">Analysis Duration</div>
          <div className={`text-sm mt-1 flex items-center justify-center gap-1 ${aiConfidence.color}`}>
            <span>{aiConfidence.icon}</span>
            <span>{aiConfidence.label}</span>
          </div>
        </div>
      </div>

      {/* AI Confidence Banner */}
      <div className={`glass p-4 rounded-lg mb-6 border-l-4 ${
        aiConfidence.level === 'High' ? 'border-green-500' :
        aiConfidence.level === 'Medium' ? 'border-yellow-500' : 'border-gray-500'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{aiConfidence.icon}</span>
            <div>
              <div className="font-semibold">
                AI Confidence: <span className={aiConfidence.color}>{aiConfidence.level}</span>
              </div>
              <div className="text-sm text-muted-foreground">{aiConfidence.details}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Analysis Quality</div>
            <div className={`font-medium ${aiConfidence.color}`}>
              {aiConfidence.level === 'High' ? '95%' : 
               aiConfidence.level === 'Medium' ? '75%' : '50%'}
            </div>
          </div>
        </div>
      </div>

      {/* Vulnerabilities List */}
      <div className="glass p-6 rounded-lg mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center justify-between">
          <span>Discovered Attack Vectors ({vulnerabilities.length})</span>
          {analysisResult?.gemini_metadata?.plan_source === 'gemini' && (
            <span className="text-xs text-green-500 flex items-center gap-1">
              <span>🤖</span> AI-Generated
            </span>
          )}
        </h3>
        {vulnerabilities.length > 0 ? (
          <div className="space-y-4">
            {vulnerabilities.map((vuln, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 border border-border/40 rounded-lg hover:border-primary/40 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-muted-foreground text-sm">Step {index + 1}</span>
                      <span className={`px-2 py-0.5 rounded text-xs border ${getSeverityColor(vuln.severity)}`}>
                        {(vuln.severity || 'unknown').toUpperCase()}
                      </span>
                    </div>
                    <h4 className="font-medium text-base">{vuln.title}</h4>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{vuln.description}</p>
                {vuln.cve && (
                  <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border/40">
                    <span className="text-xs text-primary font-mono">{vuln.cve}</span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No vulnerabilities detected in this analysis</p>
          </div>
        )}
      </div>

      {/* Latest Report Section */}
      {repoId && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4">Latest Simulation Report</h3>
          <LatestReport repoId={repoId} />
        </div>
      )}
      
      {/* Show Gemini AI Metadata if available */}
      {analysisResult?.gemini_metadata && (
        <div className="glass p-6 rounded-lg mb-6 border-l-4 border-purple-500">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">✨</span>
            <span className="gradient-text">Gemini AI Intelligence</span>
          </h3>
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div className="glass p-4 rounded-lg">
              <div className="text-xs text-muted-foreground mb-1">Analysis Method</div>
              <div className={`font-semibold text-lg ${
                analysisResult.gemini_metadata.plan_source === 'gemini' 
                  ? 'text-green-500' 
                  : 'text-yellow-500'
              }`}>
                {analysisResult.gemini_metadata.plan_source === 'gemini' ? '🤖 AI-Generated' : '⚙️ Rule-Based'}
              </div>
            </div>
            {analysisResult.gemini_metadata.model_used && (
              <div className="glass p-4 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">AI Model</div>
                <div className="font-semibold text-lg text-primary">
                  {analysisResult.gemini_metadata.model_used}
                </div>
              </div>
            )}
          </div>
          {analysisResult.gemini_metadata.ai_insight && (
            <div className="mt-4">
              <div className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                <span>💡</span>
                <span>Security Intelligence Summary</span>
              </div>
              <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 p-4 rounded-lg border border-purple-500/20">
                <p className="text-foreground leading-relaxed">
                  {analysisResult.gemini_metadata.ai_insight}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Show Gradient Task Metadata if available */}
      {analysisResult?.gradient && (
        <div className="glass p-6 rounded-lg mb-6 border-l-4 border-blue-500">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Cloud className="h-5 w-5 text-blue-500" />
            <span>Gradient Execution Environment</span>
          </h3>
          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="glass p-4 rounded-lg">
              <div className="text-xs text-muted-foreground mb-1">Task Status</div>
              <div className={`font-semibold text-lg ${
                analysisResult.gradient.status === 'success' 
                  ? 'text-green-500' 
                  : analysisResult.gradient.status === 'error'
                  ? 'text-red-500'
                  : 'text-yellow-500'
              }`}>
                {analysisResult.gradient.status?.toUpperCase() || 'UNKNOWN'}
              </div>
            </div>
            {analysisResult.gradient.metadata?.runtime_env && (
              <div className="glass p-4 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Runtime Environment</div>
                <div className="font-semibold text-sm text-primary">
                  {analysisResult.gradient.metadata.runtime_env}
                </div>
              </div>
            )}
            {analysisResult.gradient.metadata?.execution_time && (
              <div className="glass p-4 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Execution Time</div>
                <div className="font-semibold text-lg text-blue-500">
                  {analysisResult.gradient.metadata.execution_time}s
                </div>
              </div>
            )}
          </div>
          {analysisResult.gradient.metadata?.instance_type && (
            <div className="bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
              <div className="text-xs text-blue-600 dark:text-blue-400 flex items-center gap-2">
                <Server className="h-3 w-3" />
                Instance Type: {analysisResult.gradient.metadata.instance_type}
              </div>
            </div>
          )}
          {analysisResult.gradient.mock && (
            <div className="bg-yellow-500/10 p-3 rounded-lg border border-yellow-500/20 mt-3">
              <div className="text-xs text-yellow-600 dark:text-yellow-400 flex items-center gap-2">
                <AlertTriangle className="h-3 w-3" />
                Running in simulated mode for development
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link href="/dashboard">
          <Button variant="default">
            <TrendingUp className="mr-2 h-4 w-4" />
            View Dashboard
          </Button>
        </Link>
        <Button variant="outline" onClick={onNewAnalysis}>
          <RefreshCw className="mr-2 h-4 w-4" />
          New Analysis
        </Button>
        <Button 
          variant="outline" 
          onClick={handleDownloadReport}
          disabled={isDownloading}
        >
          {isDownloading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Downloading...
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              Download Report
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
}

type DemoPage = 'welcome' | 'input' | 'analysis' | 'report';

// Global flag to prevent multiple health check toasts
let healthCheckToastShown = false;

export default function DemoPage() {
  const [currentPage, setCurrentPage] = useState<DemoPage>('welcome');
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([]);
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepoId, setCurrentRepoId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const { toasts, closeToast, showSuccess, showError, showInfo } = useToast();

  // Check backend health on component mount (only once)
  useEffect(() => {
    const checkBackendHealth = async () => {
      if (healthCheckToastShown) return; // Exit if already shown globally
      
      try {
        const healthResult = await healthCheck();
        if (healthResult.success) {
          showSuccess('Backend Connected', 'CognitoForge backend is online and ready');
          healthCheckToastShown = true;
        } else {
          showInfo('Demo Mode', 'Backend unavailable - using demo simulation');
          healthCheckToastShown = true;
        }
      } catch (error) {
        showInfo('Demo Mode', 'Backend unavailable - using demo simulation');
        healthCheckToastShown = true;
      }
    };

    checkBackendHealth();
  }, []); // Empty dependency array - run only once on mount

  const startAnalysis = async (repoUrl: string, analysisType: string) => {
    setIsLoading(true);
    setCurrentPage('analysis');
    setProgress(0);
    
    // Extract repo ID from GitHub URL
    const extractRepoId = (url: string): string => {
      if (!url) return '';
      const githubPattern = /github\.com\/[^\/]+\/([^\/\?#]+)/i;
      const match = url.match(githubPattern);
      if (match && match[1]) {
        return match[1].replace(/\.git$/, '');
      }
      return url.replace(/[^a-zA-Z0-9_-]/g, '_').replace(/^_+|_+$/g, '');
    };
    
    let repoId = extractRepoId(repoUrl);
    
    // If extraction fails or is empty, generate a fallback ID
    if (!repoId) {
      repoId = `repo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    setCurrentRepoId(repoId);
    
    try {
      // First, check if backend is available
      const healthResult = await healthCheck();
      
      if (healthResult.success) {
        showSuccess('Backend Connected', 'Connected to CognitoForge backend successfully');
        
        // Initialize real backend steps
        const realSteps: AnalysisStep[] = [
          { id: '1', message: 'Uploading repository...', status: 'pending', duration: 1500 },
          { id: '2', message: 'Running AI-powered security simulation...', status: 'pending', duration: 2000 },
          { id: '3', message: 'Generating comprehensive report...', status: 'pending', duration: 2500 },
          { id: '4', message: 'Analysis complete!', status: 'pending', duration: 500 }
        ];
        setAnalysisSteps(realSteps);
        
        // Use real backend workflow
        const result = await runCompleteAnalysis(
          repoId,
          repoUrl,
          (step: string, progress: number) => {
            setProgress(progress);
            
            // Update step status based on progress
            setAnalysisSteps(prev => {
              const stepIndex = Math.floor((progress / 100) * prev.length);
              return prev.map((s, index) => {
                if (index < stepIndex) return { ...s, status: 'complete' };
                if (index === stepIndex) return { ...s, status: 'running', message: step };
                return s;
              });
            });
          }
        );
        
        if (result.success) {
          setProgress(100);
          setIsLoading(false);
          
          // Mark all steps complete
          setAnalysisSteps(prev => prev.map(s => ({ ...s, status: 'complete' })));
          
          setAnalysisResult(result.data); // Store the real backend result
          setCurrentPage('report');
          showSuccess('Analysis Complete', 'Security analysis completed with Gemini AI');
          return;
        } else {
          throw new Error(result.error?.message || 'Backend analysis failed');
        }
      } else {
        throw new Error('Backend health check failed');
      }
    } catch (error) {
      console.error('Backend analysis failed:', error);
      
      // Provide user-friendly error messages
      let errorMessage = 'Backend connection lost. Please try again.';
      if (error instanceof Error) {
        if (error.message.includes('404') || error.message.includes('Not Found')) {
          errorMessage = 'Repository not found. Please check the URL and make sure the repository is public.';
        } else if (error.message.includes('Repository not analyzed')) {
          errorMessage = 'Repository not analyzed yet. Upload and analyze it first.';
        } else {
          errorMessage = error.message;
        }
      }
      
      showError('Analysis Failed', errorMessage);
      
      // Reset state on error
      setIsLoading(false);
      setProgress(0);
      setCurrentPage('input');
      setAnalysisSteps([]);
    }
  };

  const startNewAnalysis = () => {
    setCurrentPage('welcome');
    setAnalysisSteps([]);
    setProgress(0);
    setIsLoading(false);
    setCurrentRepoId(null);
    setAnalysisResult(null);
    showSuccess('Analysis Reset', 'Ready to start a new security analysis');
  };

  const goToInputForm = () => {
    setCurrentPage('input');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <DemoHeader />
        <ToastContainer toasts={toasts} onClose={closeToast} />
        
        <main className="container mx-auto px-4 py-8">
          <AnimatePresence mode="wait">
            {currentPage === 'welcome' && (
              <motion.div
                key="welcome"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <WelcomeDashboard onStartAnalysis={goToInputForm} />
              </motion.div>
            )}
            
            {currentPage === 'input' && (
              <motion.div
                key="input"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <RepoInputForm onSubmit={startAnalysis} isLoading={isLoading} />
              </motion.div>
            )}
            
            {currentPage === 'analysis' && (
              <motion.div
                key="analysis"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <AnalysisProgress steps={analysisSteps} progress={progress} />
              </motion.div>
            )}
            
            {currentPage === 'report' && (
              <motion.div
                key="report"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <SecurityReport 
                  onNewAnalysis={startNewAnalysis} 
                  repoId={currentRepoId}
                  analysisResult={analysisResult}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </ProtectedRoute>
  );
}


