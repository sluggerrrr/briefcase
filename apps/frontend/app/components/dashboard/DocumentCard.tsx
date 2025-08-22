'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { DocumentResponse, formatFileSize, formatDate, getMimeTypeIcon } from '@/lib/documents';
import { useAuth } from '@/hooks/useAuth';
import { useDeleteDocument, useDownloadDocument } from '@/hooks/useDocuments';
import { MoreVertical, Download, Eye, Trash2, Edit, CheckCircle2, AlertTriangle, EyeOff } from 'lucide-react';
import { toast } from 'sonner';

interface DocumentCardProps {
  document: DocumentResponse;
  onEdit?: (document: DocumentResponse) => void;
  onView?: (document: DocumentResponse) => void;
}

export function DocumentCard({ document, onEdit, onView }: DocumentCardProps) {
  const { user } = useAuth();
  const deleteDocument = useDeleteDocument();
  const downloadDocument = useDownloadDocument();

  const isOwner = user?.id === document.sender_id;

  const handleDownload = async () => {
    try {
      await downloadDocument.mutateAsync(document.id);
      toast.success('Document downloaded successfully');
    } catch {
      toast.error('Failed to download document');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${document.title}"?`)) {
      return;
    }

    try {
      await deleteDocument.mutateAsync(document.id);
      toast.success('Document deleted successfully');
    } catch {
      toast.error('Failed to delete document');
    }
  };

  const getStatusBadge = () => {
    // Check if view limit is exhausted
    const isViewExhausted = document.view_limit && document.access_count >= document.view_limit;
    
    if (isViewExhausted) {
      return (
        <Badge className="bg-transparent text-sky-700 dark:text-sky-300 ring-1 ring-inset ring-sky-600/30 gap-1.5">
          <EyeOff className="h-3.5 w-3.5 text-sky-600 dark:text-sky-300" /> View limit reached
        </Badge>
      );
    }

    switch (document.status) {
      case 'active':
        return (
          <Badge className="bg-transparent text-emerald-700 dark:text-emerald-300 ring-1 ring-inset ring-emerald-600/30 gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-300" /> Active
          </Badge>
        );
      case 'expired':
        return (
          <Badge className="bg-transparent text-amber-700 dark:text-amber-300 ring-1 ring-inset ring-amber-600/30 gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-300" /> Expired
          </Badge>
        );
      case 'deleted':
        return (
          <Badge className="bg-transparent text-neutral-700 dark:text-neutral-300 ring-1 ring-inset ring-neutral-500/30">
            Deleted
          </Badge>
        );
      default:
        return <Badge variant="outline">{document.status}</Badge>;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className="text-lg">{getMimeTypeIcon(document.mime_type)}</span>
            <div className="min-w-0 flex-1">
              <h3 className="font-medium truncate" title={document.title}>
                {document.title}
              </h3>
              <p className="text-sm text-muted-foreground truncate" title={document.file_name}>
                {document.file_name}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onView?.(document)}>
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDownload} disabled={downloadDocument.isPending}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </DropdownMenuItem>
                {isOwner && (
                  <>
                    <DropdownMenuItem onClick={() => onEdit?.(document)}>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={handleDelete} 
                      disabled={deleteDocument.isPending}
                      className="text-destructive"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>Size:</span>
            <span>{formatFileSize(document.file_size)}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span>Created:</span>
            <span>{formatDate(document.created_at)}</span>
          </div>
          
          {document.expires_at && (
            <div className="flex items-center justify-between">
              <span>Expires:</span>
              <span className={new Date(document.expires_at) < new Date() ? 'text-red-500' : ''}>
                {formatDate(document.expires_at)}
              </span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span>{isOwner ? 'Recipient:' : 'Sender:'}</span>
            <span className="truncate ml-2" title={isOwner ? document.recipient_email : document.sender_email}>
              {isOwner ? (document.recipient_email || 'Unknown') : (document.sender_email || 'Unknown')}
            </span>
          </div>
          
          {document.view_limit && (
            <div className="flex items-center justify-between">
              <span>Views:</span>
              <span>
                {document.access_count} / {document.view_limit}
              </span>
            </div>
          )}
          
          {document.description && (
            <div className="pt-2 border-t">
              <p className="text-xs text-muted-foreground line-clamp-2" title={document.description}>
                {document.description}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}