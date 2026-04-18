// filepath: frontend/src/lib/api.ts
// API service for backend communication

// Get backend URL from environment variable with fallback
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

/**
 * Base API configuration
 */
export const apiConfig = {
  baseURL: BASE_URL,
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * API Error types
 */
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

/**
 * API Response wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

/**
 * Get Auth0 access token (to be called from components with useAuth0)
 * This is a helper that components can use to get tokens
 */
export let getAccessToken: (() => Promise<string>) | null = null;

/**
 * Set the token getter function (called by Auth0Provider)
 */
export function setTokenGetter(getter: () => Promise<string>) {
  getAccessToken = getter;
}

/**
 * Backend data types matching the FastAPI responses
 */
export interface UploadResponse {
  repo_id: string;
  status: string;
  source: string;
}

export interface SimulationResponse {
  repo_id: string;
  run_id: string;
  timestamp: string;
  plan: {
    repo_id: string;
    overall_severity: string;
    steps: Array<{
      step_number: number;
      description: string;
      technique_id: string;
      severity: string;
      affected_files: string[];
    }>;
  };
  sandbox: {
    repo_id: string;
    summary: string;
    logs: Array<{
      timestamp: string;
      step: number;
      action: string;
      status: string;
    }>;
  };
  // Optional AI metadata (only present when Gemini is used)
  gemini_metadata?: {
    plan_source: 'gemini' | 'fallback' | 'legacy';
    model_used?: string;
    ai_insight?: string;
    gemini_prompt?: string;
    gemini_raw_response?: string;
  };
}

export interface ReportResponse {
  repo_id: string;
  run_id: string;
  summary: {
    overall_severity: string;
    critical_steps?: number;
    high_steps?: number;
    medium_steps?: number;
    low_steps?: number;
    affected_files: string[];
  };
}

/**
 * Generic API request wrapper with error handling and Auth0 token support
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  includeAuth: boolean = false
): Promise<ApiResponse<T>> {
  const url = `${BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    ...(apiConfig.headers as Record<string, string>),
    ...(options.headers as Record<string, string>),
  };

  // Add Auth0 token if available and requested
  if (includeAuth && getAccessToken) {
    try {
      const token = await getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    } catch (error) {
      console.warn('Failed to get access token:', error);
      // Continue without token - some endpoints may not require auth
    }
  }
  
  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    return {
      success: false,
      error: {
        message: error instanceof Error ? error.message : 'Network error occurred',
        status: error instanceof Error && 'status' in error ? (error as any).status : undefined,
      }
    };
  }
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<ApiResponse<{ status: string; message?: string }>> {
  try {
    const response = await fetch(`${BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout for health check
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('Health check failed:', error);
    return {
      success: false,
      error: {
        message: error instanceof Error ? error.message : 'Health check failed',
      }
    };
  }
}

/**
 * Upload repository for analysis
 * POST /upload_repo
 */
export async function uploadRepository(repoId: string, repoUrl: string): Promise<ApiResponse<UploadResponse>> {
  return apiRequest('/upload_repo', {
    method: 'POST',
    body: JSON.stringify({
      repo_id: repoId,
      repo_url: repoUrl,
    }),
  }, false); // No auth for now
}

/**
 * Simulate attack on repository
 * POST /simulate_attack
 * @param repoId - Repository identifier
 * @param force - Force new generation, bypass 10-minute cache
 */
export async function simulateAttack(repoId: string, force: boolean = false): Promise<ApiResponse<SimulationResponse>> {
  return apiRequest('/simulate_attack', {
    method: 'POST',
    body: JSON.stringify({
      repo_id: repoId,
      force: force,
    }),
  }, false); // No auth for now
}

/**
 * Fetch latest report for repository
 * GET /reports/{repo_id}/latest
 */
export async function fetchLatestReport(repoId: string): Promise<ApiResponse<ReportResponse>> {
  return apiRequest(`/reports/${repoId}/latest`, {
    method: 'GET',
  }, false); // No auth for now
}

/**
 * Get AI-powered security insight for a repository
 * GET /api/gemini/insight/{repo_id}
 * 
 * Returns Gemini-generated analysis of repository security posture.
 * Requires USE_GEMINI=true on backend.
 * 
 * @param repoId - Repository identifier (alphanumeric, hyphens, underscores only)
 *                 If a GitHub URL is passed, use extractRepoId() from utils first
 */
export async function getGeminiInsight(repoId: string): Promise<ApiResponse<{
  repo_id: string;
  insight: string;
  source: 'simulation' | 'manifest' | 'disabled' | 'not_found' | 'error';
  run_id?: string;
  error?: string;
}>> {
  // Ensure repo_id is properly formatted (no URLs or special chars)
  const cleanRepoId = encodeURIComponent(repoId);
  
  return apiRequest(`/api/gemini/insight/${cleanRepoId}`, {
    method: 'GET',
  }, false); // No auth for now
}

/**
 * Complete analysis workflow: upload -> simulate -> fetch report
 */
export async function runCompleteAnalysis(
  repoId: string,
  repoUrl: string,
  onProgress?: (step: string, progress: number) => void
): Promise<ApiResponse<SimulationResponse>> {
  try {
    // Step 1: Upload repository
    onProgress?.('Uploading repository...', 25);
    const uploadResult = await uploadRepository(repoId, repoUrl);
    if (!uploadResult.success) {
      return {
        success: false,
        error: uploadResult.error
      };
    }

    // Step 2: Simulate attack (this has all the data we need!)
    onProgress?.('Running AI-powered security simulation...', 50);
    const simulationResult = await simulateAttack(repoId);
    if (!simulationResult.success) {
      return simulationResult;
    }

    // Step 3: Just update progress (simulation already has everything)
    onProgress?.('Generating comprehensive report...', 75);
    await new Promise(resolve => setTimeout(resolve, 500)); // Small delay for UX
    onProgress?.('Analysis complete!', 100);
    
    // Return simulation result which includes plan, gemini_metadata, and all data
    return simulationResult;
  } catch (error) {
    return {
      success: false,
      error: {
        message: error instanceof Error ? error.message : 'Analysis workflow failed',
        code: 'WORKFLOW_ERROR',
      },
    };
  }
}

/**
 * Snowflake Integration APIs
 */

export interface SnowflakeSeveritySummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

/**
 * Get severity summary from Snowflake analytics
 * GET /analytics/summary
 */
export async function getAnalyticsSummary(): Promise<ApiResponse<SnowflakeSeveritySummary>> {
  return apiRequest('/analytics/summary', {
    method: 'GET',
  }, false);
}

/**
 * Get all simulations for dashboard
 * GET /api/simulations/list
 */
export async function getAllSimulations(): Promise<ApiResponse<{
  success: boolean;
  total: number;
  simulations: SimulationResponse[];
}>> {
  return apiRequest('/api/simulations/list', {
    method: 'GET',
  }, false);
}

/**
 * Gradient Integration APIs
 */

export interface GradientStatus {
  connected: boolean;
  mock_mode: boolean;
  message: string;
}

export interface GradientTaskMetadata {
  runtime_env: string;
  instance_type: string;
  execution_time: number;
}

/**
 * Get Gradient cluster status
 * GET /api/gradient/status
 */
export async function getGradientStatus(): Promise<ApiResponse<{
  success: boolean;
  status: GradientStatus;
}>> {
  return apiRequest('/api/gradient/status', {
    method: 'GET',
  }, false);
}

export default {
  healthCheck,
  uploadRepository,
  simulateAttack,
  fetchLatestReport,
  runCompleteAnalysis,
  getGeminiInsight,
  getAnalyticsSummary,
  getAllSimulations,
  getGradientStatus,
};