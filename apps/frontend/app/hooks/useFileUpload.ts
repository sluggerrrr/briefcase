'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi, type DocumentCreate } from '@/lib/documents';
import { fileToBase64, type FileWithPreview } from '@/lib/upload-utils';

export interface UploadProgress {
  fileId: string;
  progress: number;
  status: 'preparing' | 'uploading' | 'completed' | 'error';
  error?: string;
}

export function useFileUpload() {
  const [uploadProgress, setUploadProgress] = useState<Map<string, UploadProgress>>(new Map());
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async ({ file, uploadData }: { file: FileWithPreview; uploadData: Omit<DocumentCreate, 'content' | 'file_name' | 'mime_type'> }) => {
      // Update progress to preparing
      setUploadProgress(prev => new Map(prev.set(file.id, {
        fileId: file.id,
        progress: 0,
        status: 'preparing'
      })));

      try {
        // Convert file to base64
        setUploadProgress(prev => new Map(prev.set(file.id, {
          fileId: file.id,
          progress: 25,
          status: 'preparing'
        })));

        const base64Content = await fileToBase64(file);

        setUploadProgress(prev => new Map(prev.set(file.id, {
          fileId: file.id,
          progress: 50,
          status: 'uploading'
        })));

        // Prepare document data
        const documentData: DocumentCreate = {
          ...uploadData,
          file_name: file.name,
          mime_type: file.type,
          content: base64Content,
        };

        setUploadProgress(prev => new Map(prev.set(file.id, {
          fileId: file.id,
          progress: 75,
          status: 'uploading'
        })));

        // Upload to backend
        const result = await documentsApi.uploadDocument(documentData);

        setUploadProgress(prev => new Map(prev.set(file.id, {
          fileId: file.id,
          progress: 100,
          status: 'completed'
        })));

        return result;
      } catch (error) {
        setUploadProgress(prev => new Map(prev.set(file.id, {
          fileId: file.id,
          progress: 0,
          status: 'error',
          error: error instanceof Error ? error.message : 'Upload failed'
        })));
        throw error;
      }
    },
    onSuccess: () => {
      // Invalidate documents cache to refresh the list
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const uploadFile = async (file: FileWithPreview, uploadData: Omit<DocumentCreate, 'content' | 'file_name' | 'mime_type'>) => {
    return uploadMutation.mutateAsync({ file, uploadData });
  };

  const getProgress = (fileId: string): UploadProgress | undefined => {
    return uploadProgress.get(fileId);
  };

  const clearProgress = (fileId: string) => {
    setUploadProgress(prev => {
      const newMap = new Map(prev);
      newMap.delete(fileId);
      return newMap;
    });
  };

  const clearAllProgress = () => {
    setUploadProgress(new Map());
  };

  return {
    uploadFile,
    getProgress,
    clearProgress,
    clearAllProgress,
    isUploading: uploadMutation.isPending,
  };
}