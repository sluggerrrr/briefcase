'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from './useAuth';

interface BulkOperationResult {
  document_id: string;
  status: 'success' | 'failed' | 'permission_denied';
  error?: string;
}

interface BulkOperationResponse {
  total_documents: number;
  successful: number;
  failed: number;
  results: BulkOperationResult[];
}

interface BulkShareRequest {
  document_ids: string[];
  recipient_ids: string[];
  permission_type: string;
  expires_at?: string;
}

export function useBulkOperations() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const makeRequest = async (endpoint: string, data?: any) => {
    const response = await fetch(`/api/v1/documents/${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.statusText}`);
    }

    return response.json();
  };

  // Bulk Delete Mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: async (documentIds: string[]): Promise<BulkOperationResponse> => {
      return makeRequest('bulk/delete', { document_ids: documentIds });
    },
    onSuccess: () => {
      // Invalidate document queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['accessible-documents'] });
    },
  });

  // Bulk Share Mutation
  const bulkShareMutation = useMutation({
    mutationFn: async (shareData: BulkShareRequest): Promise<BulkOperationResponse> => {
      return makeRequest('bulk/share', shareData);
    },
    onSuccess: () => {
      // Invalidate document queries and permissions
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['accessible-documents'] });
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
    },
  });

  // Bulk Download
  const bulkDownload = async (documentIds: string[]) => {
    const response = await fetch('/api/v1/documents/bulk/download', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ document_ids: documentIds }),
    });

    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'documents.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return {
    // Mutations
    bulkDelete: bulkDeleteMutation.mutateAsync,
    bulkShare: bulkShareMutation.mutateAsync,
    bulkDownload,
    
    // Loading states
    isBulkDeleting: bulkDeleteMutation.isPending,
    isBulkSharing: bulkShareMutation.isPending,
    
    // Error states
    bulkDeleteError: bulkDeleteMutation.error,
    bulkShareError: bulkShareMutation.error,
  };
}