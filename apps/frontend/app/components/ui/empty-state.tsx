'use client';

import { FileX, Upload, Users, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  title: string;
  description: string;
  variant?: 'documents' | 'search' | 'users' | 'upload' | 'generic';
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({
  title,
  description,
  variant = 'generic',
  action,
  className
}: EmptyStateProps) {
  const getIcon = () => {
    switch (variant) {
      case 'documents':
        return <FileX className="h-12 w-12 text-muted-foreground" />;
      case 'search':
        return <Search className="h-12 w-12 text-muted-foreground" />;
      case 'users':
        return <Users className="h-12 w-12 text-muted-foreground" />;
      case 'upload':
        return <Upload className="h-12 w-12 text-muted-foreground" />;
      default:
        return <FileX className="h-12 w-12 text-muted-foreground" />;
    }
  };

  return (
    <div className={cn(
      'flex flex-col items-center justify-center py-12 px-4 text-center',
      className
    )}>
      <div className="mb-4">
        {getIcon()}
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">
        {title}
      </h3>
      <p className="text-sm text-muted-foreground max-w-md mb-6">
        {description}
      </p>
      {action && (
        <Button onClick={action.onClick} className="min-w-32">
          {action.label}
        </Button>
      )}
    </div>
  );
}

// Specific empty state components for common use cases
export function NoDocumentsState({ onUpload }: { onUpload?: () => void }) {
  return (
    <EmptyState
      variant="documents"
      title="No documents yet"
      description="Upload your first document to get started with secure file sharing."
      action={onUpload ? {
        label: 'Upload Document',
        onClick: onUpload
      } : undefined}
    />
  );
}

export function NoSearchResultsState({ searchTerm }: { searchTerm: string }) {
  return (
    <EmptyState
      variant="search"
      title="No results found"
      description={`We couldn't find any documents matching "${searchTerm}". Try adjusting your search terms.`}
    />
  );
}

export function NoUsersState() {
  return (
    <EmptyState
      variant="users"
      title="No users found"
      description="There are no users available to share documents with at the moment."
    />
  );
}