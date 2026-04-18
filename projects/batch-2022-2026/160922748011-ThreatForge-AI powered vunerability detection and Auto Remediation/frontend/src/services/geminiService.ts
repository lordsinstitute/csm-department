/**
 * Gemini AI Service
 * 
 * This service provides functions to interact with the Gemini AI backend API.
 * Used for generating AI-powered insights, explanations, and security analysis.
 */

// Backend API URL from environment variables
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

/**
 * Response structure from the /api/gemini endpoint
 */
interface GeminiResponse {
  success: boolean;
  response?: string;
  model?: string;
  metadata?: {
    prompt_length: number;
    response_length: number;
    candidates: number;
  };
  error?: string;
  details?: string;
}

/**
 * Generate an AI insight using Gemini
 * 
 * Sends a prompt to the backend Gemini API and returns the AI-generated response.
 * 
 * @param prompt - The text prompt to send to Gemini AI
 * @returns Promise resolving to the AI-generated response text
 * @throws Error if the request fails or returns an error
 * 
 * @example
 * ```typescript
 * try {
 *   const insight = await generateInsight("Explain SQL injection");
 *   console.log(insight);
 * } catch (error) {
 *   console.error("Failed to generate insight:", error);
 * }
 * ```
 */
export async function generateInsight(prompt: string): Promise<string> {
  console.log('[GeminiService] Generating insight...', {
    prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
    promptLength: prompt.length,
    backendUrl: BACKEND_URL,
  });

  // Validate input
  if (!prompt || prompt.trim().length === 0) {
    const error = 'Prompt cannot be empty';
    console.error('[GeminiService] Validation error:', error);
    throw new Error(error);
  }

  try {
    // Make POST request to backend
    const response = await fetch(`${BACKEND_URL}/api/gemini`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: prompt.trim() }),
    });

    console.log('[GeminiService] Response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
    });

    // Parse JSON response
    const data: GeminiResponse = await response.json();

    console.log('[GeminiService] Response data:', {
      success: data.success,
      model: data.model,
      responseLength: data.response?.length || 0,
      metadata: data.metadata,
    });

    // Check if response was successful
    if (!response.ok || !data.success) {
      const errorMessage = data.error || `HTTP ${response.status}: ${response.statusText}`;
      const errorDetails = data.details || 'No additional details';
      
      console.error('[GeminiService] API error:', {
        error: errorMessage,
        details: errorDetails,
        status: response.status,
      });

      throw new Error(`Gemini API error: ${errorMessage}`);
    }

    // Validate response text exists
    if (!data.response) {
      const error = 'No response text received from Gemini API';
      console.error('[GeminiService] Missing response:', data);
      throw new Error(error);
    }

    console.log('[GeminiService] ✅ Insight generated successfully', {
      responseLength: data.response.length,
      model: data.model,
    });

    return data.response;

  } catch (error) {
    // Log detailed error information
    if (error instanceof Error) {
      console.error('[GeminiService] ❌ Error generating insight:', {
        name: error.name,
        message: error.message,
        stack: error.stack,
      });
      throw error;
    } else {
      console.error('[GeminiService] ❌ Unknown error:', error);
      throw new Error('An unknown error occurred while generating insight');
    }
  }
}

/**
 * Generate an insight with a timeout
 * 
 * Same as generateInsight but with a configurable timeout.
 * Useful for preventing long-running requests.
 * 
 * @param prompt - The text prompt to send to Gemini AI
 * @param timeoutMs - Timeout in milliseconds (default: 30000ms / 30s)
 * @returns Promise resolving to the AI-generated response text
 * @throws Error if the request fails, returns an error, or times out
 * 
 * @example
 * ```typescript
 * try {
 *   const insight = await generateInsightWithTimeout("Explain XSS", 15000);
 *   console.log(insight);
 * } catch (error) {
 *   console.error("Request timed out or failed:", error);
 * }
 * ```
 */
export async function generateInsightWithTimeout(
  prompt: string,
  timeoutMs: number = 30000
): Promise<string> {
  console.log('[GeminiService] Generating insight with timeout:', {
    timeoutMs,
  });

  return Promise.race([
    generateInsight(prompt),
    new Promise<string>((_, reject) =>
      setTimeout(
        () => reject(new Error(`Request timed out after ${timeoutMs}ms`)),
        timeoutMs
      )
    ),
  ]);
}

/**
 * Check if the Gemini service is available
 * 
 * Sends a simple test request to verify the backend API is reachable.
 * 
 * @returns Promise resolving to true if service is available, false otherwise
 * 
 * @example
 * ```typescript
 * const isAvailable = await checkGeminiAvailability();
 * if (isAvailable) {
 *   console.log("Gemini service is ready");
 * }
 * ```
 */
export async function checkGeminiAvailability(): Promise<boolean> {
  console.log('[GeminiService] Checking availability...');

  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
    });

    const isAvailable = response.ok;
    
    console.log('[GeminiService] Availability check:', {
      available: isAvailable,
      status: response.status,
    });

    return isAvailable;
  } catch (error) {
    console.error('[GeminiService] Availability check failed:', error);
    return false;
  }
}

/**
 * Batch generate insights for multiple prompts
 * 
 * Generates insights for multiple prompts sequentially.
 * Note: Requests are made one at a time to avoid rate limiting.
 * 
 * @param prompts - Array of prompts to process
 * @returns Promise resolving to array of responses (or errors)
 * 
 * @example
 * ```typescript
 * const prompts = ["Explain SQL injection", "What is XSS?"];
 * const results = await batchGenerateInsights(prompts);
 * results.forEach((result, index) => {
 *   if (result.success) {
 *     console.log(`Prompt ${index + 1}:`, result.response);
 *   } else {
 *     console.error(`Prompt ${index + 1} failed:`, result.error);
 *   }
 * });
 * ```
 */
export async function batchGenerateInsights(
  prompts: string[]
): Promise<Array<{ success: boolean; response?: string; error?: string }>> {
  console.log('[GeminiService] Batch generating insights:', {
    count: prompts.length,
  });

  const results: Array<{ success: boolean; response?: string; error?: string }> = [];

  for (let i = 0; i < prompts.length; i++) {
    const prompt = prompts[i];
    console.log(`[GeminiService] Processing prompt ${i + 1}/${prompts.length}`);

    try {
      const response = await generateInsight(prompt);
      results.push({ success: true, response });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error(`[GeminiService] Prompt ${i + 1} failed:`, errorMessage);
      results.push({ success: false, error: errorMessage });
    }

    // Small delay between requests to avoid rate limiting
    if (i < prompts.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }

  console.log('[GeminiService] Batch complete:', {
    total: results.length,
    successful: results.filter(r => r.success).length,
    failed: results.filter(r => !r.success).length,
  });

  return results;
}

// Export types for use in components
export type { GeminiResponse };
