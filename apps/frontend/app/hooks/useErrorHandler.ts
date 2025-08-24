/**
 * Custom hook for centralized error handling with user-friendly messages
 */

import { useCallback } from 'react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { 
  getErrorMessage, 
  isAuthError, 
  extractFieldErrors,
  type ErrorMessage 
} from '@/lib/error-messages';

export interface UseErrorHandlerOptions {
  /** Show toast notification on error */
  showToast?: boolean;
  /** Redirect to login on auth errors */
  redirectOnAuth?: boolean;
  /** Custom error handler function */
  onError?: (error: unknown, errorMessage: ErrorMessage) => void;
  /** Extract field errors for forms */
  extractFields?: boolean;
}

export interface ErrorHandlerResult {
  /** Handle error with toast and/or custom logic */
  handleError: (error: unknown, options?: UseErrorHandlerOptions) => void;
  /** Get formatted error message without side effects */
  getFormattedError: (error: unknown) => ErrorMessage;
  /** Check if error is authentication related */
  isAuthenticationError: (error: unknown) => boolean;
  /** Extract field-specific errors for form validation */
  getFieldErrors: (error: unknown) => Record<string, string>;
}

export function useErrorHandler(defaultOptions: UseErrorHandlerOptions = {}): ErrorHandlerResult {
  const router = useRouter();

  const handleError = useCallback((error: unknown, options: UseErrorHandlerOptions = {}) => {
    const config = { ...defaultOptions, ...options };
    const errorMessage = getErrorMessage(error);

    console.error('Error handled:', {
      originalError: error,
      formattedError: errorMessage,
      timestamp: new Date().toISOString()
    });

    // Show toast notification
    if (config.showToast !== false) {
      toast.error(errorMessage.title, {
        description: errorMessage.description,
        action: errorMessage.action ? {
          label: errorMessage.action,
          onClick: () => {
            // Handle common actions
            switch (errorMessage.action) {
              case 'Try again':
                window.location.reload();
                break;
              case 'Log in again':
              case 'Log in':
                router.push('/auth/login');
                break;
              case 'Go back':
                router.back();
                break;
              case 'Check connection':
                toast.info('Please check your internet connection and try again');
                break;
              case 'Contact support':
                toast.info('Please contact support for assistance');
                break;
              default:
                // Custom action - let parent component handle
                break;
            }
          }
        } : undefined,
        duration: 5000,
      });
    }

    // Handle authentication errors
    if (config.redirectOnAuth !== false && isAuthError(error)) {
      // Clear any stored tokens using the proper auth storage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('briefcase_token');
        localStorage.removeItem('briefcase_refresh_token');
        localStorage.removeItem('briefcase_token_expires_at');
        localStorage.removeItem('briefcase_user');
      }
      
      // Redirect to login after a brief delay to show the toast
      setTimeout(() => {
        router.push('/auth/login');
      }, 1500);
    }

    // Call custom error handler
    if (config.onError) {
      config.onError(error, errorMessage);
    }

  }, [defaultOptions, router]);

  const getFormattedError = useCallback((error: unknown): ErrorMessage => {
    return getErrorMessage(error);
  }, []);

  const isAuthenticationError = useCallback((error: unknown): boolean => {
    return isAuthError(error);
  }, []);

  const getFieldErrors = useCallback((error: unknown): Record<string, string> => {
    return extractFieldErrors(error);
  }, []);

  return {
    handleError,
    getFormattedError,
    isAuthenticationError,
    getFieldErrors
  };
}

/**
 * Hook for handling form-specific errors with field validation
 */
export function useFormErrorHandler(defaultOptions: UseErrorHandlerOptions = {}) {
  const errorHandler = useErrorHandler(defaultOptions);
  
  const handleFormError = useCallback((error: unknown, setFieldError?: (field: string, message: string) => void) => {
    const fieldErrors = errorHandler.getFieldErrors(error);
    
    // Set individual field errors if setFieldError function is provided
    if (setFieldError && Object.keys(fieldErrors).length > 0) {
      Object.entries(fieldErrors).forEach(([field, message]) => {
        setFieldError(field, message);
      });
      
      // Don't show toast for field validation errors since they're shown inline
      errorHandler.handleError(error, { ...defaultOptions, showToast: false });
    } else {
      // Show toast for general form errors
      errorHandler.handleError(error, defaultOptions);
    }
  }, [errorHandler, defaultOptions]);

  return {
    ...errorHandler,
    handleFormError
  };
}

/**
 * Hook for API mutation error handling with React Query
 */
export function useMutationErrorHandler(defaultOptions: UseErrorHandlerOptions = {}) {
  const errorHandler = useErrorHandler(defaultOptions);

  const getMutationErrorHandler = useCallback(() => {
    return (error: unknown) => {
      errorHandler.handleError(error, defaultOptions);
    };
  }, [errorHandler, defaultOptions]);

  return {
    ...errorHandler,
    onError: getMutationErrorHandler()
  };
}