'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { DocumentResponse, formatFileSize, formatDate, getMimeTypeIcon } from '@/lib/documents';
import { useAuth } from '@/hooks/useAuth';
import { useDownloadDocument, useDeleteDocument } from '@/hooks/useDocuments';
import { Download, Trash2, Calendar, User, FileText, Activity } from 'lucide-react';
import { toast } from 'sonner';

interface DocumentDetailsProps {
  document: DocumentResponse;
  open: boolean;
  onClose: () => void;
}

export function DocumentDetails({ document, open, onClose }: DocumentDetailsProps) {
  const { user } = useAuth();
  const downloadDocument = useDownloadDocument();
  const deleteDocument = useDeleteDocument();

  const isOwner = user?.id === document.sender_id;

  const handleDownload = async () => {
    try {
      await downloadDocument.mutateAsync(document.id);
      toast.success('Document downloaded successfully');
    } catch {
      // Error is handled by the mutation's error handler
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${document.title}"?`)) {
      return;
    }

    try {
      await deleteDocument.mutateAsync(document.id);
      toast.success('Document deleted successfully');
      onClose();
    } catch {
      // Error is handled by the mutation's error handler
    }
  };

  const getStatusInfo = () => {
    const isExpired = document.expires_at && new Date(document.expires_at) < new Date();
    const isViewLimitReached = document.view_limit && document.access_count >= document.view_limit;

    if (document.status === 'deleted') {
      return { color: 'bg-gray-500', text: 'Deleted', description: 'This document has been deleted' };
    }
    if (isExpired) {
      return { color: 'bg-red-500', text: 'Expired', description: 'This document has expired' };
    }
    if (isViewLimitReached) {
      return { color: 'bg-orange-500', text: 'View Limit Reached', description: 'Maximum view limit has been reached' };
    }
    return { color: 'bg-green-500', text: 'Active', description: 'Document is accessible' };
  };

  const statusInfo = getStatusInfo();

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-2xl">{getMimeTypeIcon(document.mime_type)}</span>
            <div>
              <div className="text-lg font-semibold">{document.title}</div>
              <div className="text-sm font-normal text-muted-foreground">{document.file_name}</div>
            </div>
          </DialogTitle>
          <DialogDescription>
            Document details and access information
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className={`${statusInfo.color} text-white`}>
              {statusInfo.text}
            </Badge>
            <span className="text-sm text-muted-foreground">{statusInfo.description}</span>
          </div>

          {/* Description */}
          {document.description && (
            <div>
              <h4 className="font-medium mb-2">Description</h4>
              <p className="text-sm text-muted-foreground bg-muted p-3 rounded">
                {document.description}
              </p>
            </div>
          )}

          <Separator />

          {/* Document Information */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                File Information
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">File name:</span>
                  <span className="font-mono text-right break-all">{document.file_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">File size:</span>
                  <span>{formatFileSize(document.file_size)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Type:</span>
                  <span className="font-mono">{document.mime_type}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <User className="h-4 w-4" />
                People
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sender:</span>
                  <span className="text-right break-all">{document.sender_email || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Recipient:</span>
                  <span className="text-right break-all">{document.recipient_email || 'Unknown'}</span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Timestamps and Limits */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Timeline
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created:</span>
                  <span>{formatDate(document.created_at)}</span>
                </div>
                {document.expires_at && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Expires:</span>
                    <span className={new Date(document.expires_at) < new Date() ? 'text-red-500' : ''}>
                      {formatDate(document.expires_at)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Access Control
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Access count:</span>
                  <span>{document.access_count}</span>
                </div>
                {document.view_limit && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">View limit:</span>
                    <span>{document.view_limit}</span>
                  </div>
                )}
                {document.view_limit && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Remaining:</span>
                    <span className={document.access_count >= document.view_limit ? 'text-red-500' : 'text-green-600'}>
                      {Math.max(0, document.view_limit - document.access_count)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <Separator />

          {/* Actions */}
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button 
                onClick={handleDownload} 
                disabled={downloadDocument.isPending || document.status !== 'active'}
                size="sm"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>

            {isOwner && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={deleteDocument.isPending}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}