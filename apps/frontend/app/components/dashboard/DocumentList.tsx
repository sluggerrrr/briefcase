'use client';

import { useState } from 'react';
import { useDocuments } from '@/hooks/useDocuments';
import { DocumentCard } from './DocumentCard';
import { DocumentFilters } from './DocumentFilters';
import { DocumentDetails } from './DocumentDetails';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DocumentResponse } from '@/lib/documents';
import { AlertCircle, FileX } from 'lucide-react';

interface DocumentListProps {
  className?: string;
}

export function DocumentList({ className }: DocumentListProps) {
  const [showSent, setShowSent] = useState(true);
  const [showReceived, setShowReceived] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedDocument, setSelectedDocument] = useState<DocumentResponse | null>(null);

  const { data: documents, isLoading, error } = useDocuments(showSent, showReceived);

  // Filter documents based on search and filters
  const filteredDocuments = documents?.filter(doc => {
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      if (!doc.title.toLowerCase().includes(search) &&
          !doc.file_name.toLowerCase().includes(search) &&
          !doc.sender_email.toLowerCase().includes(search) &&
          !doc.recipient_email.toLowerCase().includes(search)) {
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
            <div key={i} className="space-y-3">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-20 w-full" />
            </div>
          ))}
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="text-center py-12">
          <FileX className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium text-muted-foreground mb-2">
            {documents?.length === 0 ? 'No documents yet' : 'No documents match your filters'}
          </h3>
          <p className="text-sm text-muted-foreground">
            {documents?.length === 0 
              ? 'Upload your first document to get started'
              : 'Try adjusting your search or filter criteria'
            }
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map(document => (
            <DocumentCard
              key={document.id}
              document={document}
              onView={setSelectedDocument}
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
    </div>
  );
}