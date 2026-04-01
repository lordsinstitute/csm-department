// filepath: c:\workspace\CognitoForge-Ai\src\lib\api.ts
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
 * Generic API request wrapper with error handling and Auth0 token support
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  includeAuth: boolean = true
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
 * Health check endpoint (no auth required)
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
 * Upload repository for analysis (requires auth)
 */
export async function uploadRepository(repoUrl: string, analysisType: string): Promise<ApiResponse<{ repoId: string; message: string }>> {
  return apiRequest('/api/upload', {
    method: 'POST',
    body: JSON.stringify({
      repoUrl,
      analysisType,
    }),
  }, true); // Include auth token
}

/**
 * Start security analysis simulation (requires auth)
 */
export async function startAnalysis(repoId: string, config: any): Promise<ApiResponse<{ analysisId: string; status: string }>> {
  return apiRequest('/api/simulate', {
    method: 'POST',
    body: JSON.stringify({
      repoId,
      config,
    }),
  }, true); // Include auth token
}

/**
 * Get latest analysis report (requires auth)
 */
export async function getLatestReport(repoId?: string): Promise<ApiResponse<any>> {
  const endpoint = repoId ? `/api/reports/${repoId}` : '/api/reports/latest';
  return apiRequest(endpoint, {
    method: 'GET',
  }, true); // Include auth token
}

/**
 * Get analysis status (requires auth)
 */
export async function getAnalysisStatus(analysisId: string): Promise<ApiResponse<{ status: string; progress: number }>> {
  return apiRequest(`/api/analysis/${analysisId}/status`, {
    method: 'GET',
  }, true); // Include auth token
}

/**
 * Download analysis report (requires auth)
 */
export async function downloadReport(reportId: string, format: 'pdf' | 'json' = 'pdf') {
  const headers: HeadersInit = {
    'Accept': format === 'pdf' ? 'application/pdf' : 'application/json',
  };

  // Add auth token if available
  if (getAccessToken) {
    try {
      const token = await getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    } catch (error) {
      console.warn('Failed to get access token for download:', error);
    }
  }

  const response = await fetch(`${BASE_URL}/api/reports/${reportId}/download?format=${format}`, {
    method: 'GET',
    headers,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to download report: ${response.status}`);
  }
  
  return response.blob();
}

export default {
  healthCheck,
  uploadRepository,
  startAnalysis,
  getLatestReport,
  getAnalysisStatus,
  downloadReport,
};