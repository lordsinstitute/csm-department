// filepath: frontend/src/components/reports/LatestReport.tsx
'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, AlertTriangle, CheckCircle, AlertCircle, Info, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { fetchLatestReport, ReportResponse } from '@/lib/api';

interface LatestReportProps {
  repoId: string;
  className?: string;
}

export function LatestReport({ repoId, className = '' }: LatestReportProps) {
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const { showSuccess, showError } = useToast();

  const fetchReport = async () => {
    setIsLoading(true);
    setError('');

    try {
      const result = await fetchLatestReport(repoId);
      
      if (result.success && result.data) {
        setReport(result.data);
        showSuccess('Report Loaded', 'Latest simulation report fetched successfully');
      } else {
        const errorMsg = result.error?.message || 'Failed to fetch report';
        setError(errorMsg);
        showError('Report Error', errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Network error occurred';
      setError(errorMsg);
      showError('Network Error', errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (repoId) {
      fetchReport();
    }
  }, [repoId]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'high':
        return <AlertCircle className="h-5 w-5 text-orange-500" />;
      case 'medium':
        return <Info className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="h-5 w-5 text-blue-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'high':
        return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'low':
        return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      default:
        return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-lg ${className}`}>
        <div className="flex items-center justify-center h-40">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 text-primary animate-spin mx-auto mb-2" />
            <p className="text-muted-foreground">Loading latest report...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !report) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-lg ${className}`}>
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Failed to Load Report</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button 
            onClick={fetchReport} 
            variant="outline"
            disabled={isLoading}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-lg ${className}`}>
        <div className="text-center">
          <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No Report Available</h3>
          <p className="text-muted-foreground mb-4">No simulation report found for this repository</p>
          <Button 
            onClick={fetchReport} 
            variant="outline"
            disabled={isLoading}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Check Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          {getSeverityIcon(report.summary?.overall_severity || 'medium')}
          <div>
            <h2 className="text-xl font-bold text-foreground">Latest Simulation Report</h2>
            <p className="text-sm text-muted-foreground">
              Report ID: {report.run_id || 'N/A'}
            </p>
          </div>
        </div>
        <Button 
          onClick={fetchReport} 
          variant="outline" 
          size="sm"
          disabled={isLoading}
        >
          {isLoading ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Overall Severity */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-foreground">Overall Severity:</span>
          <span className={`px-2 py-1 rounded-md text-xs font-medium border ${getSeverityColor(report.summary?.overall_severity || 'medium')}`}>
            {(report.summary?.overall_severity || 'MEDIUM').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Summary Counts */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-500">{report.summary?.critical_steps || 0}</div>
          <div className="text-xs text-red-400">Critical</div>
        </div>
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-orange-500">{report.summary?.high_steps || 0}</div>
          <div className="text-xs text-orange-400">High</div>
        </div>
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-yellow-500">{report.summary?.medium_steps || 0}</div>
          <div className="text-xs text-yellow-400">Medium</div>
        </div>
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-500">{report.summary?.low_steps || 0}</div>
          <div className="text-xs text-blue-400">Low</div>
        </div>
      </div>

      {/* Affected Files */}
      <div>
        <h3 className="text-lg font-semibold text-foreground mb-3">
          Affected Files ({(report.summary?.affected_files || []).length})
        </h3>
        
        {(!report.summary?.affected_files || report.summary.affected_files.length === 0) ? (
          <div className="text-center py-8">
            <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-muted-foreground">No issues found in any files</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {report.summary.affected_files.map((filePath: string, index: number) => (
              <div 
                key={index}
                className="bg-white/5 border border-white/10 rounded-lg p-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium text-foreground">{filePath}</span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor('medium')}`}>
                    AFFECTED
                  </span>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  File identified in security analysis
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}