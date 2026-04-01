// Example usage of the improved CognitoForge components

// 1. Import the necessary components and utilities
import { useToast } from '@/components/ui/toast';
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { uploadRepository, simulateAttack, fetchLatestReport } from '@/lib/api';
import { validateRepoUrl, validateAnalysisType } from '@/lib/validation';

// 2. Example component showing how to use the API with proper error handling
function ExampleApiUsage() {
  const { showSuccess, showError, showInfo } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const handleUploadRepo = async (repoUrl: string, analysisType: string) => {
    // Validate inputs first
    const repoValidation = validateRepoUrl(repoUrl);
    const analysisValidation = validateAnalysisType(analysisType);
    
    if (!repoValidation.isValid) {
      showError('Validation Error', repoValidation.errors.join(', '));
      return;
    }

    if (!analysisValidation.isValid) {
      showError('Validation Error', analysisValidation.errors.join(', '));
      return;
    }

    setIsLoading(true);
    showInfo('Uploading Repository', 'Connecting to backend...');

    try {
      const result = await uploadRepository(repoUrl, analysisType);
      
      if (result.success) {
        showSuccess('Repository Uploaded', 'Analysis will begin shortly');
        // Continue with next step...
      } else {
        showError('Upload Failed', result.error?.message || 'Unknown error occurred');
      }
    } catch (error) {
      showError('Network Error', 'Failed to connect to backend');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Your form or UI components here */}
      <button 
        onClick={() => handleUploadRepo('https://github.com/user/repo', 'comprehensive')}
        disabled={isLoading}
      >
        {isLoading ? 'Uploading...' : 'Upload Repository'}
      </button>
    </div>
  );
}

// 3. Example form validation usage
function ExampleFormValidation() {
  const [repoUrl, setRepoUrl] = useState('');
  const [errors, setErrors] = useState<string[]>([]);

  const handleRepoUrlChange = (value: string) => {
    setRepoUrl(value);
    
    // Validate on change
    const validation = validateRepoUrl(value);
    setErrors(validation.errors);
  };

  return (
    <div>
      <input
        type="text"
        value={repoUrl}
        onChange={(e) => handleRepoUrlChange(e.target.value)}
        className={`border ${errors.length > 0 ? 'border-red-500' : 'border-gray-300'}`}
        placeholder="Enter repository URL"
      />
      
      {errors.length > 0 && (
        <div className="text-red-500 text-sm mt-1">
          {errors.map((error, index) => (
            <div key={index}>{error}</div>
          ))}
        </div>
      )}
    </div>
  );
}

export { ExampleApiUsage, ExampleFormValidation };