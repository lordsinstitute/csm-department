// filepath: frontend/src/lib/validation.ts

/**
 * Validation utilities for forms
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Validate repository URL
 */
export function validateRepoUrl(url: string): ValidationResult {
  const errors: string[] = [];

  if (!url || url.trim().length === 0) {
    errors.push('Repository URL is required');
  } else {
    // Basic URL validation
    try {
      const urlObj = new URL(url);
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        errors.push('Repository URL must use http or https protocol');
      }
      
      // Check if it looks like a git repository URL
      const validHosts = ['github.com', 'gitlab.com', 'bitbucket.org'];
      const isValidHost = validHosts.some(host => urlObj.hostname.includes(host));
      
      if (!isValidHost && !urlObj.pathname.endsWith('.git')) {
        errors.push('Please provide a valid Git repository URL');
      }
    } catch {
      errors.push('Please provide a valid URL');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate repository ID
 */
export function validateRepoId(repoId: string): ValidationResult {
  const errors: string[] = [];

  if (!repoId || repoId.trim().length === 0) {
    errors.push('Repository ID is required');
  } else {
    // Only allow alphanumeric characters, hyphens, and underscores
    const validPattern = /^[a-zA-Z0-9_-]+$/;
    if (!validPattern.test(repoId)) {
      errors.push('Repository ID can only contain letters, numbers, hyphens, and underscores');
    }

    if (repoId.length < 3) {
      errors.push('Repository ID must be at least 3 characters long');
    }

    if (repoId.length > 50) {
      errors.push('Repository ID must be less than 50 characters');
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate analysis type
 */
export function validateAnalysisType(analysisType: string): ValidationResult {
  const errors: string[] = [];
  const validTypes = ['comprehensive', 'quick', 'cicd', 'dependencies'];

  if (!analysisType || analysisType.trim().length === 0) {
    errors.push('Analysis type is required');
  } else if (!validTypes.includes(analysisType)) {
    errors.push('Please select a valid analysis type');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Combine multiple validation results
 */
export function combineValidationResults(...results: ValidationResult[]): ValidationResult {
  const allErrors = results.flatMap(result => result.errors);
  return {
    isValid: allErrors.length === 0,
    errors: allErrors
  };
}