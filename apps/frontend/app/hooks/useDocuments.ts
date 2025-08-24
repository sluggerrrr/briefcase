'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi, type DocumentUpdate, type DocumentResponse } from '@/lib/documents';
import { useMutationErrorHandler } from './useErrorHandler';

export function useDocuments(sent: boolean = true, received: boolean = true) {
  return useQuery({
    queryKey: ['documents', { sent, received }],
    queryFn: () => documentsApi.getDocuments(sent, received),
    staleTime: 5 * 1000, // 5 seconds - shorter for more frequent updates
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    refetchInterval: 30 * 1000, // Auto-refetch every 30 seconds
    refetchIntervalInBackground: false, // Don't refetch when tab is not active
  });
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['documents', documentId],
    queryFn: () => documentsApi.getDocument(documentId),
    enabled: !!documentId,
    staleTime: 10 * 1000, // 10 seconds - shorter for more frequent updates
    refetchOnWindowFocus: true,
  });
}

export function useDocumentContent(documentId: string, enabled: boolean = false) {
  return useQuery({
    queryKey: ['documents', documentId, 'content'],
    queryFn: () => documentsApi.getDocumentContent(documentId),
    enabled: !!documentId && enabled,
    staleTime: 0, // Always fresh for content
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();
  const { onError: handleError } = useMutationErrorHandler();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      documentsApi.updateDocument(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: ['documents'] });
      
      // Snapshot the previous values
      const previousDocuments = queryClient.getQueriesData({ queryKey: ['documents'] });
      
      // Optimistically update the cache
      queryClient.setQueriesData(
        { queryKey: ['documents'], exact: false },
        (oldData: DocumentResponse[]) => {
          if (!oldData || !Array.isArray(oldData)) return oldData;
          return oldData.map((doc: DocumentResponse) => 
            doc.id === id ? { ...doc, ...data, updated_at: new Date().toISOString() } : doc
          );
        }
      );
      
      // Return context with snapshotted values
      return { previousDocuments };
    },
    onError: (err, _variables, context) => {
      // Revert optimistic updates on error
      if (context?.previousDocuments) {
        context.previousDocuments.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
      // Handle error with user-friendly message
      handleError(err);
    },
    onSuccess: (updatedDocument) => {
      // Update the document in the cache with server response
      queryClient.setQueryData(['documents', updatedDocument.id], updatedDocument);
      
      // Update the document in all documents list queries with actual server data
      queryClient.setQueriesData(
        { queryKey: ['documents'], exact: false },
        (oldData: DocumentResponse[]) => {
          if (!oldData || !Array.isArray(oldData)) return oldData;
          return oldData.map((doc: DocumentResponse) => 
            doc.id === updatedDocument.id ? updatedDocument : doc
          );
        }
      );
    },
    onSettled: () => {
      // Always refetch after error or success to ensure we have fresh data
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  const { onError: handleError } = useMutationErrorHandler();

  return useMutation({
    mutationFn: (documentId: string) => documentsApi.deleteDocument(documentId),
    onMutate: async (documentId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['documents'] });
      
      // Snapshot previous values
      const previousDocuments = queryClient.getQueriesData({ queryKey: ['documents'] });
      
      // Optimistically remove the document from all lists
      queryClient.setQueriesData(
        { queryKey: ['documents'], exact: false },
        (oldData: DocumentResponse[]) => {
          if (!oldData || !Array.isArray(oldData)) return oldData;
          return oldData.filter((doc: DocumentResponse) => doc.id !== documentId);
        }
      );
      
      return { previousDocuments };
    },
    onError: (err, documentId, context) => {
      // Revert optimistic updates on error
      if (context?.previousDocuments) {
        context.previousDocuments.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
      // Handle error with user-friendly message
      handleError(err);
    },
    onSuccess: (_, documentId) => {
      // Remove document from individual cache
      queryClient.removeQueries({ queryKey: ['documents', documentId] });
    },
    onSettled: () => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDownloadDocument() {
  const queryClient = useQueryClient();
  const { onError: handleError } = useMutationErrorHandler();

  return useMutation({
    mutationFn: (documentId: string) => documentsApi.downloadDocument(documentId),
    onSuccess: (blob) => {
      // Derive a safe random filename that does not expose document identifiers
      const generateRandomFileName = (length: number = 12): string => {
        const array = new Uint8Array(length);
        crypto.getRandomValues(array);
        const alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let name = '';
        for (let i = 0; i < array.length; i++) {
          name += alphabet[array[i] % alphabet.length];
        }
        return name;
      };

      const guessExtensionFromMime = (mimeType: string | undefined): string => {
        switch (mimeType) {
          case 'application/pdf':
            return 'pdf';
          case 'image/png':
            return 'png';
          case 'image/jpeg':
            return 'jpg';
          case 'image/gif':
            return 'gif';
          case 'text/plain':
            return 'txt';
          case 'application/zip':
            return 'zip';
          case 'application/msword':
            return 'doc';
          case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return 'docx';
          case 'application/vnd.ms-excel':
            return 'xls';
          case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            return 'xlsx';
          case 'application/vnd.ms-powerpoint':
            return 'ppt';
          case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            return 'pptx';
          default:
            return 'bin';
        }
      };

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const randomName = generateRandomFileName();
      const extension = guessExtensionFromMime(blob.type);
      a.download = `${randomName}.${extension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
    onError: handleError,
    onSettled: () => {
      // Refetch documents to update access counts after download
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}