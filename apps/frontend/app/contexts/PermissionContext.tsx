'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

interface UserPermissions {
  roles: string[];
  documentPermissions: Record<string, string[]>; // document_id -> permissions
}

interface PermissionContextType {
  permissions: UserPermissions | null;
  isLoading: boolean;
  error: string | null;
  hasRole: (role: string) => boolean;
  hasDocumentPermission: (documentId: string, permission: string) => boolean;
  canPerformBulkOperation: (operation: string, documentIds: string[]) => boolean;
  refreshPermissions: () => Promise<void>;
}

const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

export function PermissionProvider({ children }: { children: React.ReactNode }) {
  const { user, token } = useAuth();
  const [permissions, setPermissions] = useState<UserPermissions | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasRole = (role: string): boolean => {
    if (!permissions) return false;
    return permissions.roles.includes(role) || permissions.roles.includes('admin');
  };

  const hasDocumentPermission = (documentId: string, permission: string): boolean => {
    if (!permissions || !documentId) return false;
    
    const docPermissions = permissions.documentPermissions[documentId];
    return docPermissions ? docPermissions.includes(permission) : false;
  };

  const canPerformBulkOperation = (operation: string, documentIds: string[]): boolean => {
    if (!permissions || documentIds.length === 0) return false;
    
    return documentIds.every(id => hasDocumentPermission(id, operation));
  };

  const refreshPermissions = async (): Promise<void> => {
    if (!user || !token) {
      setPermissions(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/permissions/users/me/permissions', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch permissions: ${response.statusText}`);
      }

      const data = await response.json();
      setPermissions(data);
    } catch (err) {
      console.error('Failed to fetch permissions:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch permissions');
      setPermissions(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user && token) {
      refreshPermissions();
    } else {
      setPermissions(null);
      setError(null);
    }
  }, [user, token]);

  const value: PermissionContextType = {
    permissions,
    isLoading,
    error,
    hasRole,
    hasDocumentPermission,
    canPerformBulkOperation,
    refreshPermissions,
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
}

export const usePermissions = (): PermissionContextType => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermissions must be used within a PermissionProvider');
  }
  return context;
};

// Hook for checking specific document permissions
export const useDocumentPermissions = (documentId: string) => {
  const { hasDocumentPermission, permissions } = usePermissions();

  return {
    canView: hasDocumentPermission(documentId, 'read'),
    canEdit: hasDocumentPermission(documentId, 'write'),
    canShare: hasDocumentPermission(documentId, 'share'),
    canDelete: hasDocumentPermission(documentId, 'delete'),
    canManagePermissions: hasDocumentPermission(documentId, 'admin'),
    permissions: permissions?.documentPermissions[documentId] || [],
  };
};

// Hook for bulk operation permissions
export const useBulkOperationPermissions = (documentIds: string[]) => {
  const { canPerformBulkOperation } = usePermissions();

  return {
    canBulkView: canPerformBulkOperation('read', documentIds),
    canBulkEdit: canPerformBulkOperation('write', documentIds),
    canBulkShare: canPerformBulkOperation('share', documentIds),
    canBulkDelete: canPerformBulkOperation('delete', documentIds),
    canBulkManage: canPerformBulkOperation('admin', documentIds),
  };
};