/**
 * Comprehensive error message mapping system for Briefcase application
 * Maps backend error messages to user-friendly messages with i18n support
 */

export interface ErrorMessage {
  title: string;
  description: string;
  action?: string;
}

export interface ErrorMessageMap {
  [key: string]: ErrorMessage;
}

/**
 * Authentication error messages
 */
export const authErrorMessages: ErrorMessageMap = {
  'Incorrect email or password': {
    title: 'Login Failed',
    description: 'The email address or password you entered is incorrect. Please check your credentials and try again.',
    action: 'Try again'
  },
  'Account is disabled': {
    title: 'Account Disabled',
    description: 'Your account has been disabled. Please contact support for assistance.',
    action: 'Contact support'
  },
  'Email already registered': {
    title: 'Email Already in Use',
    description: 'An account with this email address already exists. Please use a different email or try logging in.',
    action: 'Try logging in'
  },
  'Invalid refresh token': {
    title: 'Session Expired',
    description: 'Your session has expired. Please log in again to continue.',
    action: 'Log in again'
  },
  'User not found or inactive': {
    title: 'Account Not Found',
    description: 'Your account could not be found or is inactive. Please check your credentials.',
    action: 'Check credentials'
  }
};

/**
 * Document-related error messages
 */
export const documentErrorMessages: ErrorMessageMap = {
  'Document not found': {
    title: 'Document Not Found',
    description: 'The document you\'re looking for doesn\'t exist or has been removed.',
    action: 'Go back'
  },
  'User not authorized to access this document': {
    title: 'Access Denied',
    description: 'You don\'t have permission to access this document. Only the sender and recipient can view it.',
    action: 'Contact sender'
  },
  'User not authorized or document not accessible': {
    title: 'Document Unavailable',
    description: 'This document is no longer accessible. It may have expired or reached its view limit.',
    action: 'Request new link'
  },
  'Not authorized to access this document or document has expired': {
    title: 'Document Unavailable',
    description: 'This document is no longer accessible. It may have expired or reached its view limit.',
    action: 'Request new link'
  },
  'Only sender can update document metadata': {
    title: 'Update Permission Required',
    description: 'Only the person who shared this document can modify its settings.',
    action: 'Contact sender'
  },
  'Only sender can delete document': {
    title: 'Delete Permission Required',
    description: 'Only the person who shared this document can delete it.',
    action: 'Contact sender'
  },
  'Failed to process document content': {
    title: 'Processing Error',
    description: 'There was a problem processing the document content. Please try again.',
    action: 'Try again'
  },
  'Decryption failed': {
    title: 'Decryption Error',
    description: 'Unable to decrypt the document. The file may be corrupted or the security key is invalid.',
    action: 'Contact support'
  }
};

/**
 * File upload and validation error messages
 */
export const fileErrorMessages: ErrorMessageMap = {
  'File size exceeds 10MB limit': {
    title: 'File Too Large',
    description: 'The selected file is too large. Please choose a file smaller than 10MB.',
    action: 'Select smaller file'
  },
  'Expiration date must be in the future': {
    title: 'Invalid Expiration Date',
    description: 'The expiration date must be set to a future date.',
    action: 'Choose future date'
  },
  'Expiration date cannot be more than 1 year in the future': {
    title: 'Expiration Date Too Far',
    description: 'Documents cannot be set to expire more than 1 year from now.',
    action: 'Choose earlier date'
  },
  'Password must be at least 8 characters long': {
    title: 'Password Too Short',
    description: 'Your password must contain at least 8 characters for security.',
    action: 'Use longer password'
  }
};

/**
 * Network and server error messages
 */
export const networkErrorMessages: ErrorMessageMap = {
  'Network Error': {
    title: 'Connection Problem',
    description: 'Unable to connect to the server. Please check your internet connection.',
    action: 'Check connection'
  },
  'Failed to fetch': {
    title: 'Server Unavailable',
    description: 'The server is currently unavailable. Please try again in a few moments.',
    action: 'Try again later'
  },
  'Request timeout': {
    title: 'Request Timed Out',
    description: 'The request took too long to complete. Please try again.',
    action: 'Try again'
  }
};

/**
 * Generic error messages for unknown errors
 */
export const genericErrorMessages: ErrorMessageMap = {
  'unknown': {
    title: 'Something Went Wrong',
    description: 'An unexpected error occurred. Our team has been notified and will investigate.',
    action: 'Try again'
  },
  'validation': {
    title: 'Invalid Input',
    description: 'Please check your input and make sure all required fields are filled correctly.',
    action: 'Check input'
  },
  'server': {
    title: 'Server Error',
    description: 'A server error occurred while processing your request. Please try again later.',
    action: 'Try again later'
  }
};

/**
 * HTTP status code to error message mapping
 */
export const statusCodeMessages: ErrorMessageMap = {
  '400': {
    title: 'Bad Request',
    description: 'The request was invalid. Please check your input and try again.',
    action: 'Check input'
  },
  '401': {
    title: 'Authentication Required',
    description: 'You need to log in to access this resource.',
    action: 'Log in'
  },
  '403': {
    title: 'Access Forbidden',
    description: 'You don\'t have permission to perform this action.',
    action: 'Contact support'
  },
  '404': {
    title: 'Not Found',
    description: 'The requested resource could not be found.',
    action: 'Go back'
  },
  '409': {
    title: 'Conflict',
    description: 'There was a conflict with the current state. Please refresh and try again.',
    action: 'Refresh page'
  },
  '422': {
    title: 'Validation Error',
    description: 'The submitted data is invalid. Please check your input.',
    action: 'Check input'
  },
  '429': {
    title: 'Too Many Requests',
    description: 'You\'re making too many requests. Please wait a moment before trying again.',
    action: 'Wait and retry'
  },
  '500': {
    title: 'Server Error',
    description: 'An internal server error occurred. Our team has been notified.',
    action: 'Try again later'
  },
  '502': {
    title: 'Service Unavailable',
    description: 'The service is temporarily unavailable. Please try again later.',
    action: 'Try again later'
  },
  '503': {
    title: 'Service Unavailable',
    description: 'The service is under maintenance. Please try again later.',
    action: 'Try again later'
  }
};

/**
 * Get user-friendly error message from backend error
 * @param error - Error object from API response
 * @returns Formatted error message object
 */
export function getErrorMessage(error: unknown): ErrorMessage {
  // Handle different error formats
  let errorDetail: string | undefined;
  let statusCode: string | undefined;

  // Type guard for error with response property
  if (error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { data?: { detail?: string }; status?: number } };
    if (errorWithResponse.response?.data?.detail) {
      errorDetail = errorWithResponse.response.data.detail;
      statusCode = errorWithResponse.response.status?.toString();
    }
  }
  
  // Type guard for error with detail property
  if (!errorDetail && error && typeof error === 'object' && 'detail' in error) {
    const errorWithDetail = error as { detail?: string; status_code?: number };
    errorDetail = errorWithDetail.detail;
    statusCode = errorWithDetail.status_code?.toString();
  }
  
  // Type guard for error with message property
  if (!errorDetail && error && typeof error === 'object' && 'message' in error) {
    const errorWithMessage = error as { message?: string };
    errorDetail = errorWithMessage.message;
  }
  
  // Handle string errors
  if (!errorDetail && typeof error === 'string') {
    errorDetail = error;
  }

  // Get status code for axios errors
  if (!statusCode && error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { status?: number } };
    if (errorWithResponse.response?.status) {
      statusCode = errorWithResponse.response.status.toString();
    }
  }

  // Look for specific error message matches
  if (errorDetail) {
    // Check authentication errors
    for (const [key, message] of Object.entries(authErrorMessages)) {
      if (errorDetail.includes(key)) {
        return message;
      }
    }

    // Check document errors
    for (const [key, message] of Object.entries(documentErrorMessages)) {
      if (errorDetail.includes(key)) {
        return message;
      }
    }

    // Check file errors
    for (const [key, message] of Object.entries(fileErrorMessages)) {
      if (errorDetail.includes(key)) {
        return message;
      }
    }

    // Check network errors
    for (const [key, message] of Object.entries(networkErrorMessages)) {
      if (errorDetail.includes(key)) {
        return message;
      }
    }
  }

  // Fall back to status code messages
  if (statusCode && statusCodeMessages[statusCode]) {
    return statusCodeMessages[statusCode];
  }

  // Handle validation errors (array of errors)
  if (error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { data?: { detail?: unknown } } };
    if (Array.isArray(errorWithResponse.response?.data?.detail)) {
      return {
        title: 'Validation Error',
        description: 'Please check the highlighted fields and correct any errors.',
        action: 'Fix errors'
      };
    }
  }

  // Default fallback
  return genericErrorMessages.unknown;
}

/**
 * Format error for toast notifications
 * @param error - Error object
 * @returns Formatted string for toast
 */
export function formatErrorForToast(error: unknown): string {
  const errorMessage = getErrorMessage(error);
  return errorMessage.description;
}

/**
 * Check if error indicates authentication failure
 * @param error - Error object
 * @returns True if auth error
 */
export function isAuthError(error: unknown): boolean {
  let statusCode: number | undefined;
  let errorDetail: string | undefined;
  
  // Get status code
  if (error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { status?: number } };
    statusCode = errorWithResponse.response?.status;
  }
  if (!statusCode && error && typeof error === 'object' && 'status_code' in error) {
    const errorWithStatus = error as { status_code?: number };
    statusCode = errorWithStatus.status_code;
  }
  
  // Get error detail
  if (error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { data?: { detail?: string } } };
    errorDetail = errorWithResponse.response?.data?.detail;
  }
  if (!errorDetail && error && typeof error === 'object' && 'detail' in error) {
    const errorWithDetail = error as { detail?: string };
    errorDetail = errorWithDetail.detail;
  }
  if (!errorDetail && error && typeof error === 'object' && 'message' in error) {
    const errorWithMessage = error as { message?: string };
    errorDetail = errorWithMessage.message;
  }
  
  if (statusCode === 401) return true;
  
  if (typeof errorDetail === 'string') {
    return errorDetail.includes('token') || 
           errorDetail.includes('unauthorized') || 
           errorDetail.includes('authentication');
  }
  
  return false;
}

/**
 * Extract field-specific validation errors
 * @param error - Error object
 * @returns Object with field names as keys and error messages as values
 */
export function extractFieldErrors(error: unknown): Record<string, string> {
  let detail: unknown;
  
  // Get detail from error
  if (error && typeof error === 'object' && 'response' in error) {
    const errorWithResponse = error as { response?: { data?: { detail?: unknown } } };
    detail = errorWithResponse.response?.data?.detail;
  }
  if (!detail && error && typeof error === 'object' && 'detail' in error) {
    const errorWithDetail = error as { detail?: unknown };
    detail = errorWithDetail.detail;
  }
  
  const fieldErrors: Record<string, string> = {};

  if (Array.isArray(detail)) {
    for (const err of detail) {
      if (err && typeof err === 'object' && 'loc' in err && 'msg' in err) {
        const errorWithFields = err as { loc: unknown[]; msg: string };
        if (Array.isArray(errorWithFields.loc) && errorWithFields.loc.length > 0) {
          const fieldName = errorWithFields.loc[errorWithFields.loc.length - 1];
          if (typeof fieldName === 'string') {
            fieldErrors[fieldName] = errorWithFields.msg;
          }
        }
      }
    }
  }

  return fieldErrors;
}