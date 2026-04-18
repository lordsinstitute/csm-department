// filepath: frontend/src/components/HealthCheck.tsx
'use client';

import { useEffect, useState } from 'react';
import { healthCheck } from '@/lib/api';
import { AlertTriangle, CheckCircle, X } from 'lucide-react';

export function HealthCheck() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy' | 'dismissed'>('checking');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const result = await healthCheck();
        if (result.success) {
          setHealthStatus('healthy');
          // Auto-dismiss healthy status after 3 seconds
          setTimeout(() => {
            setHealthStatus('dismissed');
          }, 3000);
        } else {
          setHealthStatus('unhealthy');
          setError(result.error?.message || 'Backend connection failed');
        }
      } catch (err) {
        console.error('Backend health check failed:', err);
        setHealthStatus('unhealthy');
        setError(err instanceof Error ? err.message : 'Backend connection failed');
      }
    };

    checkBackendHealth();
  }, []);

  // Don't render anything if dismissed or still checking
  if (healthStatus === 'dismissed' || healthStatus === 'checking') {
    return null;
  }

  const handleDismiss = () => {
    setHealthStatus('dismissed');
  };

  const handleRetry = async () => {
    setHealthStatus('checking');
    setError('');
    
    try {
      const result = await healthCheck();
      if (result.success) {
        setHealthStatus('healthy');
        setTimeout(() => {
          setHealthStatus('dismissed');
        }, 3000);
      } else {
        setHealthStatus('unhealthy');
        setError(result.error?.message || 'Backend connection failed');
      }
    } catch (err) {
      console.error('Backend health check failed:', err);
      setHealthStatus('unhealthy');
      setError(err instanceof Error ? err.message : 'Backend connection failed');
    }
  };

  return (
    <div className="fixed top-20 right-4 z-40 max-w-sm">
      {healthStatus === 'healthy' && (
        <div className="bg-green-900/80 border border-green-700/50 text-green-100 px-4 py-3 rounded-lg backdrop-blur-md flex items-center gap-3 shadow-lg">
          <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">Backend Connected</p>
            <p className="text-xs text-green-300">API is healthy and ready</p>
          </div>
          <button 
            onClick={handleDismiss}
            className="text-green-400 hover:text-green-300 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {healthStatus === 'unhealthy' && (
        <div className="bg-red-900/80 border border-red-700/50 text-red-100 px-4 py-3 rounded-lg backdrop-blur-md flex items-center gap-3 shadow-lg">
          <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">Backend Unavailable</p>
            <p className="text-xs text-red-300">{error}</p>
            <button 
              onClick={handleRetry}
              className="text-xs text-red-200 hover:text-red-100 underline mt-1"
            >
              Retry connection
            </button>
          </div>
          <button 
            onClick={handleDismiss}
            className="text-red-400 hover:text-red-300 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}