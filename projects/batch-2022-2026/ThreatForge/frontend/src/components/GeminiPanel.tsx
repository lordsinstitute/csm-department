'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Send, Loader2, Terminal, Copy, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generateInsight } from '@/services/geminiService';

export function GeminiPanel() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleAnalysis = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setResponse('');

    try {
      const result = await generateInsight(prompt);
      setResponse(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate AI analysis';
      setError(errorMessage);
      console.error('Gemini Analysis Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (response) {
      await navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleAnalysis();
    }
  };

  const examplePrompts = [
    'Analyze security vulnerabilities in authentication flow',
    'Review this code for potential SQL injection risks',
    'Explain OWASP Top 10 security risks in simple terms',
    'Best practices for securing API endpoints'
  ];

  const handleExampleClick = (example: string) => {
    setPrompt(example);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center gap-3 mb-6"
      >
        <div className="p-3 bg-gradient-to-br from-purple-600/20 to-violet-600/20 rounded-xl border border-purple-500/30">
          <Sparkles className="h-7 w-7 text-purple-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-foreground flex items-center gap-2">
            Gemini AI Security Analyst
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Powered by gemini-2.5-flash
            </span>
          </h2>
          <p className="text-sm text-muted-foreground">
            AI-powered security insights and vulnerability analysis
          </p>
        </div>
      </motion.div>

      {/* Example Prompts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="glass rounded-xl p-4 border border-purple-500/20"
      >
        <h3 className="text-sm font-medium text-purple-300 mb-3 flex items-center gap-2">
          <Terminal className="h-4 w-4" />
          Try these prompts:
        </h3>
        <div className="flex flex-wrap gap-2">
          {examplePrompts.map((example, idx) => (
            <button
              key={idx}
              onClick={() => handleExampleClick(example)}
              className="text-xs px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 hover:text-purple-200 border border-purple-500/30 hover:border-purple-500/50 transition-all duration-200"
            >
              {example}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="glass rounded-xl p-6 border border-purple-500/30 space-y-4"
      >
        <div className="space-y-2">
          <label className="text-sm font-medium text-purple-300 flex items-center gap-2">
            <Terminal className="h-4 w-4" />
            Security Analysis Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g., Analyze this authentication flow for security vulnerabilities..."
            className="w-full h-32 px-4 py-3 bg-black/60 border border-purple-500/30 rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all resize-none font-mono text-sm"
            disabled={loading}
          />
          <p className="text-xs text-muted-foreground">
            Press <kbd className="px-2 py-0.5 bg-purple-500/10 rounded border border-purple-500/30">Ctrl</kbd> + <kbd className="px-2 py-0.5 bg-purple-500/10 rounded border border-purple-500/30">Enter</kbd> to run analysis
          </p>
        </div>

        <Button
          onClick={handleAnalysis}
          disabled={loading || !prompt.trim()}
          className="w-full"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Analyzing with Gemini AI...
            </>
          ) : (
            <>
              <Send className="mr-2 h-5 w-5" />
              Run Gemini Analysis
            </>
          )}
        </Button>
      </motion.div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="glass rounded-xl p-4 border border-red-500/30 bg-red-500/5"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-red-400 mb-1">Analysis Failed</h4>
                <p className="text-sm text-red-300/80">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Response Display */}
      <AnimatePresence>
        {response && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            className="glass rounded-xl border border-purple-500/30 overflow-hidden"
          >
            {/* Response Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-purple-500/20 bg-gradient-to-r from-purple-600/10 to-violet-600/10">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <Sparkles className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-purple-300">AI Security Analysis</h3>
                  <p className="text-xs text-muted-foreground">Generated by Gemini 2.5 Flash</p>
                </div>
              </div>
              <Button
                onClick={handleCopy}
                variant="ghost"
                size="sm"
                className="text-purple-300 hover:text-purple-200"
              >
                {copied ? (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy
                  </>
                )}
              </Button>
            </div>

            {/* Response Content */}
            <div className="relative">
              {/* Cyber grid background */}
              <div className="absolute inset-0 opacity-5 pointer-events-none">
                <div className="absolute inset-0" style={{
                  backgroundImage: `
                    linear-gradient(rgba(147, 51, 234, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(147, 51, 234, 0.1) 1px, transparent 1px)
                  `,
                  backgroundSize: '20px 20px'
                }} />
              </div>

              <div className="relative max-h-96 overflow-y-auto p-6 scrollbar-custom">
                <pre className="font-mono text-sm text-purple-100 whitespace-pre-wrap leading-relaxed">
                  {response}
                </pre>
              </div>

              {/* Gradient fade at bottom */}
              <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black/80 to-transparent pointer-events-none" />
            </div>

            {/* Response Footer */}
            <div className="px-6 py-3 border-t border-purple-500/20 bg-black/40">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Response length: {response.length} characters</span>
                <div className="flex items-center gap-2">
                  <span className="inline-flex h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                  <span>Live AI Analysis</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Animation */}
      <AnimatePresence>
        {loading && !response && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-xl p-8 border border-purple-500/30 text-center"
          >
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="h-16 w-16 rounded-full border-4 border-purple-500/20 border-t-purple-500 animate-spin" />
                <Sparkles className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-6 w-6 text-purple-400 animate-pulse" />
              </div>
              <div className="space-y-2">
                <p className="text-lg font-semibold text-purple-300">Analyzing with Gemini AI...</p>
                <p className="text-sm text-muted-foreground">Please wait while we generate your security insights</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center text-xs text-muted-foreground pt-4"
      >
        <p>Powered by Google Gemini 2.5 Flash • Real-time AI security analysis</p>
      </motion.div>
    </div>
  );
}
