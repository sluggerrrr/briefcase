import { apiClient } from './auth';

export interface DocumentResponse {
  id: string;
  title: string;
  description?: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  sender_id: string;
  sender_email?: string;
  recipient_id: string;
  recipient_email?: string;
  status: 'active' | 'expired' | 'deleted';
  created_at: string;
  expires_at?: string;
  view_limit?: number;
  access_count: number;
}

export interface DocumentContentResponse {
  id: string;
  title: string;
  file_name: string;
  mime_type: string;
  content: string; // base64 encoded
  access_count: number;
  view_limit?: number;
}

export interface DocumentCreate {
  title: string;
  description?: string;
  file_name: string;
  mime_type: string;
  content: string; // base64 encoded
  recipient_id: string;
  expires_at?: string;
  view_limit?: number;
}

export interface DocumentUpdate {
  title?: string;
  description?: string;
  expires_at?: string;
  view_limit?: number;
}

export const documentsApi = {
  async getDocuments(sent: boolean = true, received: boolean = true): Promise<DocumentResponse[]> {
    const params = new URLSearchParams();
    if (sent) params.append('sent', 'true');
    if (received) params.append('received', 'true');
    
    return apiClient.request<DocumentResponse[]>(`/api/v1/documents?${params.toString()}`);
  },

  async getDocument(documentId: string): Promise<DocumentResponse> {
    return apiClient.request<DocumentResponse>(`/api/v1/documents/${documentId}`);
  },

  async downloadDocument(documentId: string): Promise<Blob> {
    const token = localStorage.getItem('briefcase_token');
    const response = await fetch(`${apiClient.baseURL}/api/v1/documents/${documentId}/download`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    });

    if (!response.ok) {
      let errorMessage = `Download failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // If parsing fails, use the default error message
      }
      throw new Error(errorMessage);
    }

    return response.blob();
  },

  async getDocumentContent(documentId: string): Promise<DocumentContentResponse> {
    return apiClient.request<DocumentContentResponse>(`/api/v1/documents/${documentId}/content`);
  },

  async updateDocument(documentId: string, data: DocumentUpdate): Promise<DocumentResponse> {
    return apiClient.request<DocumentResponse>(`/api/v1/documents/${documentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return apiClient.request<{ message: string }>(`/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
  },

  async uploadDocument(data: DocumentCreate): Promise<DocumentResponse> {
    return apiClient.request<DocumentResponse>('/api/v1/documents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'active':
      return 'bg-green-500';
    case 'expired':
      return 'bg-red-500';
    case 'deleted':
      return 'bg-gray-500';
    default:
      return 'bg-gray-500';
  }
};

export const getMimeTypeIcon = (mimeType: string | null): string => {
  if (!mimeType) return 'File';
  if (mimeType.startsWith('image/')) return 'Image';
  if (mimeType.includes('pdf')) return 'FileText';
  if (mimeType.includes('word') || mimeType.includes('document')) return 'FileText';
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'Table';
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return 'Presentation';
  if (mimeType.includes('zip') || mimeType.includes('archive')) return 'Archive';
  return 'File';
};