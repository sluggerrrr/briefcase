'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi, type DocumentUpdate } from '@/lib/documents';

export function useDocuments(sent: boolean = true, received: boolean = true) {
  return useQuery({
    queryKey: ['documents', { sent, received }],
    queryFn: () => documentsApi.getDocuments(sent, received),
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: false,
  });
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['documents', documentId],
    queryFn: () => documentsApi.getDocument(documentId),
    enabled: !!documentId,
    staleTime: 60 * 1000, // 1 minute
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

  return useMutation({
    mutationFn: ({ documentId, data }: { documentId: string; data: DocumentUpdate }) =>
      documentsApi.updateDocument(documentId, data),
    onSuccess: (updatedDocument) => {
      // Update the document in the cache
      queryClient.setQueryData(['documents', updatedDocument.id], updatedDocument);
      
      // Invalidate documents list to refresh
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => documentsApi.deleteDocument(documentId),
    onSuccess: (_, documentId) => {
      // Remove document from cache
      queryClient.removeQueries({ queryKey: ['documents', documentId] });
      
      // Invalidate documents list to refresh
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDownloadDocument() {
  return useMutation({
    mutationFn: (documentId: string) => documentsApi.downloadDocument(documentId),
    onSuccess: (blob, documentId) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-${documentId}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });
}