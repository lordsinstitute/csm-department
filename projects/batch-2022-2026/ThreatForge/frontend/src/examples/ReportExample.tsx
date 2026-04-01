// filepath: frontend/src/examples/ReportExample.tsx
'use client';

import { useState } from 'react';
import { LatestReport } from '@/components/reports';
import { Button } from '@/components/ui/button';

export function ReportExample() {
  const [repoId, setRepoId] = useState('demo-repo-123');

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Simulation Report Example</h1>
        <p className="text-muted-foreground mb-6">
          This demonstrates the LatestReport component with a sample repository ID
        </p>
        
        {/* Repository ID Input */}
        <div className="flex gap-2 justify-center mb-6">
          <input
            type="text"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
            placeholder="Enter repository ID"
            className="px-3 py-2 border border-border rounded-lg bg-background text-foreground"
          />
          <Button onClick={() => setRepoId(repoId)}>
            Load Report
          </Button>
        </div>
      </div>

      {/* Report Component */}
      <LatestReport repoId={repoId} />
      
      {/* Usage Instructions */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <h3 className="font-semibold text-blue-400 mb-2">Usage:</h3>
        <pre className="text-sm text-blue-300 whitespace-pre-wrap">
{`import { LatestReport } from '@/components/reports';

// Basic usage
<LatestReport repoId="your-repo-id" />

// With custom styling
<LatestReport 
  repoId="your-repo-id" 
  className="max-w-2xl mx-auto" 
/>`}
        </pre>
      </div>
    </div>
  );
}