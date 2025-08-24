'use client';

import { useState } from 'react';
import { useDocuments } from '@/hooks/useDocuments';
import { DocumentCard } from './DocumentCard';
import { DocumentFilters } from './DocumentFilters';
import { DocumentDetails } from './DocumentDetails';
import { ShareDocumentDialog } from './ShareDocumentDialog';
import { DocumentCardSkeleton } from '@/components/ui/loading-skeleton';
import { NoDocumentsState, NoSearchResultsState } from '@/components/ui/empty-state';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DocumentResponse } from '@/lib/documents';
import { AlertCircle } from 'lucide-react';

interface DocumentListProps {
  className?: string;
}

export function DocumentList({ className }: DocumentListProps) {
  const [showSent, setShowSent] = useState(true);
  const [showReceived, setShowReceived] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedDocument, setSelectedDocument] = useState<DocumentResponse | null>(null);
  const [shareDocument, setShareDocument] = useState<DocumentResponse | null>(null);

  const { data: documents, isLoading, error } = useDocuments(showSent, showReceived);

  // Filter documents based on search and filters
  const filteredDocuments = documents?.filter(doc => {
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      if (!doc.title.toLowerCase().includes(search) &&
          !doc.file_name.toLowerCase().includes(search) &&
          !doc.sender_email?.toLowerCase().includes(search) &&
          !doc.recipient_email?.toLowerCase().includes(search)) {
        return false;
      }
    }

    // Status filter
    if (statusFilter !== 'all' && doc.status !== statusFilter) {
      return false;
    }

    return true;
  }) || [];

  if (error) {
    return (
      <Alert variant="destructive" className={className}>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load documents. Please try again later.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={className}>
      <DocumentFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        showSent={showSent}
        onShowSentChange={setShowSent}
        showReceived={showReceived}
        onShowReceivedChange={setShowReceived}
        documentCount={filteredDocuments.length}
        totalCount={documents?.length || 0}
      />

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <DocumentCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredDocuments.length === 0 ? (
        documents?.length === 0 ? (
          <NoDocumentsState />
        ) : (
          <NoSearchResultsState searchTerm={searchTerm} />
        )
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map(document => (
            <DocumentCard
              key={document.id}
              document={document}
              onView={setSelectedDocument}
              onShare={setShareDocument}
            />
          ))}
        </div>
      )}

      {selectedDocument && (
        <DocumentDetails
          document={selectedDocument}
          open={!!selectedDocument}
          onClose={() => setSelectedDocument(null)}
        />
      )}

      {shareDocument && (
        <ShareDocumentDialog
          open={!!shareDocument}
          onOpenChange={(open) => !open && setShareDocument(null)}
          document={shareDocument}
        />
      )}
    </div>
  );
}