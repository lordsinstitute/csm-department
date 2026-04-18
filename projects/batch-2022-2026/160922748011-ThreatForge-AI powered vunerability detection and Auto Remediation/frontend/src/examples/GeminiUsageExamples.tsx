/**
 * Example React Component using Gemini Service
 * 
 * This demonstrates how to use the geminiService in a React component.
 * You can copy this code into any component where you need AI insights.
 */

'use client';

import { useState } from 'react';
import { generateInsight, generateInsightWithTimeout } from '@/services/geminiService';

export function GeminiInsightExample() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setResponse('');

    try {
      // Option 1: Basic usage
      const insight = await generateInsight(prompt);
      
      // Option 2: With timeout (uncomment to use)
      // const insight = await generateInsightWithTimeout(prompt, 15000);
      
      setResponse(insight);
      console.log('✅ Insight received:', insight);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate insight';
      setError(errorMessage);
      console.error('❌ Error:', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Gemini AI Insights</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium mb-2">
            Ask Gemini AI
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Explain SQL injection attacks"
            className="w-full p-3 border rounded-lg min-h-[100px]"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !prompt.trim()}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate Insight'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {response && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="font-semibold mb-2">AI Response:</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
        </div>
      )}

      {loading && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-600">🤖 Gemini is thinking...</p>
        </div>
      )}
    </div>
  );
}

// Example: Using in a simpler inline way
export function SimpleGeminiButton() {
  const [insight, setInsight] = useState('');

  const askGemini = async () => {
    try {
      const response = await generateInsight("What are the top 3 web security vulnerabilities?");
      setInsight(response);
    } catch (error) {
      console.error('Failed to get insight:', error);
    }
  };

  return (
    <div>
      <button onClick={askGemini}>
        Get Security Insights
      </button>
      {insight && <p>{insight}</p>}
    </div>
  );
}

// Example: Using in an existing component
export function SecurityAnalysisWithAI({ codeSnippet }: { codeSnippet: string }) {
  const [analysis, setAnalysis] = useState('');

  const analyzeCode = async () => {
    const prompt = `Analyze this code for security vulnerabilities:\n\n${codeSnippet}`;
    
    try {
      const result = await generateInsight(prompt);
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  return (
    <div>
      <button onClick={analyzeCode}>Analyze with AI</button>
      {analysis && (
        <div className="analysis-result">
          {analysis}
        </div>
      )}
    </div>
  );
}
