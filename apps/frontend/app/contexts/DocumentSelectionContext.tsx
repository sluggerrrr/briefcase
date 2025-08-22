'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

interface DocumentSelectionContextType {
  selectedDocuments: Set<string>;
  isDocumentSelected: (documentId: string) => boolean;
  toggleDocumentSelection: (documentId: string) => void;
  selectDocument: (documentId: string) => void;
  deselectDocument: (documentId: string) => void;
  selectAllDocuments: (documentIds: string[]) => void;
  clearSelection: () => void;
  getSelectedDocumentIds: () => string[];
  selectedCount: number;
  isSelectionMode: boolean;
  setSelectionMode: (enabled: boolean) => void;
}

const DocumentSelectionContext = createContext<DocumentSelectionContextType | undefined>(undefined);

export function DocumentSelectionProvider({ children }: { children: React.ReactNode }) {
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [isSelectionMode, setIsSelectionMode] = useState(false);

  const isDocumentSelected = useCallback((documentId: string): boolean => {
    return selectedDocuments.has(documentId);
  }, [selectedDocuments]);

  const toggleDocumentSelection = useCallback((documentId: string) => {
    setSelectedDocuments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(documentId)) {
        newSet.delete(documentId);
      } else {
        newSet.add(documentId);
      }
      return newSet;
    });
  }, []);

  const selectDocument = useCallback((documentId: string) => {
    setSelectedDocuments(prev => new Set(prev).add(documentId));
  }, []);

  const deselectDocument = useCallback((documentId: string) => {
    setSelectedDocuments(prev => {
      const newSet = new Set(prev);
      newSet.delete(documentId);
      return newSet;
    });
  }, []);

  const selectAllDocuments = useCallback((documentIds: string[]) => {
    setSelectedDocuments(new Set(documentIds));
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedDocuments(new Set());
  }, []);

  const getSelectedDocumentIds = useCallback((): string[] => {
    return Array.from(selectedDocuments);
  }, [selectedDocuments]);

  const setSelectionMode = useCallback((enabled: boolean) => {
    setIsSelectionMode(enabled);
    if (!enabled) {
      clearSelection();
    }
  }, [clearSelection]);

  const value: DocumentSelectionContextType = {
    selectedDocuments,
    isDocumentSelected,
    toggleDocumentSelection,
    selectDocument,
    deselectDocument,
    selectAllDocuments,
    clearSelection,
    getSelectedDocumentIds,
    selectedCount: selectedDocuments.size,
    isSelectionMode,
    setSelectionMode,
  };

  return (
    <DocumentSelectionContext.Provider value={value}>
      {children}
    </DocumentSelectionContext.Provider>
  );
}

export const useDocumentSelection = (): DocumentSelectionContextType => {
  const context = useContext(DocumentSelectionContext);
  if (!context) {
    throw new Error('useDocumentSelection must be used within a DocumentSelectionProvider');
  }
  return context;
};