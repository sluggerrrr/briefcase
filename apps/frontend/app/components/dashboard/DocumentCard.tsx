'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { DocumentResponse, formatFileSize, formatDate, getMimeTypeIcon } from '@/lib/documents';
import { useAuth } from '@/hooks/useAuth';
import { useDeleteDocument, useDownloadDocument } from '@/hooks/useDocuments';
import { useDocumentPermissions } from '@/contexts/PermissionContext';
import { useDocumentSelection } from '@/contexts/DocumentSelectionContext';
import { MoreVertical, Download, Eye, Trash2, Edit, CheckCircle2, AlertTriangle, EyeOff, Share2, Settings, Shield, Image, FileText, Table, Presentation, Archive, File } from 'lucide-react';
import { toast } from 'sonner';

interface DocumentCardProps {
  document: DocumentResponse;
  onEdit?: (document: DocumentResponse) => void;
  onView?: (document: DocumentResponse) => void;
  onShare?: (document: DocumentResponse) => void;
  onManagePermissions?: (document: DocumentResponse) => void;
}

const getFileIcon = (mimeType: string) => {
  const iconName = getMimeTypeIcon(mimeType);
  switch (iconName) {
    case 'Image': return Image;
    case 'FileText': return FileText;
    case 'Table': return Table;
    case 'Presentation': return Presentation;
    case 'Archive': return Archive;
    default: return File;
  }
};

export function DocumentCard({ 
  document, 
  onEdit, 
  onView, 
  onShare, 
  onManagePermissions 
}: DocumentCardProps) {
  const { user } = useAuth();
  const deleteDocument = useDeleteDocument();
  const downloadDocument = useDownloadDocument();
  
  const {
    canView,
    canEdit,
    canShare,
    canDelete,
    canManagePermissions,
    permissions
  } = useDocumentPermissions(document.id);

  const {
    isSelectionMode,
    isDocumentSelected,
    toggleDocumentSelection
  } = useDocumentSelection();

  const isOwner = user?.id === document.sender_id;
  const isSelected = isDocumentSelected(document.id);
  const FileIcon = getFileIcon(document.mime_type);

  const handleDownload = async () => {
    if (!canView) {
      toast.error('You do not have permission to download this document');
      return;
    }

    try {
      await downloadDocument.mutateAsync(document.id);
      toast.success('Document downloaded successfully');
    } catch {
      toast.error('Failed to download document');
    }
  };

  const handleDelete = async () => {
    if (!canDelete) {
      toast.error('You do not have permission to delete this document');
      return;
    }

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

  const handleEdit = () => {
    if (!canEdit) {
      toast.error('You do not have permission to edit this document');
      return;
    }
    onEdit?.(document);
  };

  const handleShare = () => {
    if (!canShare) {
      toast.error('You do not have permission to share this document');
      return;
    }
    onShare?.(document);
  };

  const handleManagePermissions = () => {
    if (!canManagePermissions) {
      toast.error('You do not have permission to manage permissions for this document');
      return;
    }
    onManagePermissions?.(document);
  };

  const getStatusBadge = () => {
    // Check if view limit is exhausted
    const isViewExhausted = document.view_limit && document.access_count >= document.view_limit;
    
    if (isViewExhausted) {
      return (
        <Badge className="!bg-sky-50 !text-sky-800 ring-1 ring-inset ring-sky-600/20 dark:!bg-sky-900/30 dark:!text-sky-300 dark:ring-sky-600/30 gap-2 px-3 py-1.5 text-sm font-semibold">
          <EyeOff className="h-4 w-4 !text-sky-600 dark:!text-sky-300" /> View limit reached
        </Badge>
      );
    }

    switch (document.status) {
      case 'active':
        return (
          <Badge className="!bg-emerald-50 !text-emerald-800 ring-1 ring-inset ring-emerald-600/20 dark:!bg-emerald-900/30 dark:!text-emerald-300 dark:ring-emerald-600/30 gap-2 px-3 py-1.5 text-sm font-semibold">
            <CheckCircle2 className="h-4 w-4 !text-emerald-600 dark:!text-emerald-300" /> Active
          </Badge>
        );
      case 'expired':
        return (
          <Badge className="!bg-amber-50 !text-amber-800 ring-1 ring-inset ring-amber-600/20 dark:!bg-amber-900/30 dark:!text-amber-300 dark:ring-amber-600/30 gap-2 px-3 py-1.5 text-sm font-semibold">
            <AlertTriangle className="h-4 w-4 !text-amber-600 dark:!text-amber-300" /> Expired
          </Badge>
        );
      case 'deleted':
        return (
          <Badge className="!bg-neutral-100 !text-neutral-800 ring-1 ring-inset ring-neutral-500/20 dark:!bg-neutral-900/30 dark:!text-neutral-300 dark:ring-neutral-500/30 px-3 py-1.5 text-sm font-semibold">
            Deleted
          </Badge>
        );
      default:
        return <Badge variant="outline">{document.status}</Badge>;
    }
  };

  return (
    <Card 
      className={`hover:shadow-lg transition-all duration-200 hover:scale-[1.02] ${
        isSelected ? 'ring-2 ring-primary bg-primary/5' : ''
      } ${isSelectionMode ? 'cursor-pointer hover:bg-muted/50' : ''}`}
      onClick={() => isSelectionMode && toggleDocumentSelection(document.id)}
    >
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-3">
          {/* Selection Checkbox */}
          {isSelectionMode && (
            <div className="mr-3 mt-1">
              <Checkbox
                checked={isSelected}
                onCheckedChange={() => toggleDocumentSelection(document.id)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}
          
          <div className="flex items-start gap-3 min-w-0 flex-1">
            <div className="flex-shrink-0 mt-1">
              <FileIcon className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-lg font-semibold truncate mb-1" title={document.title}>
                {document.title}
              </h3>
              <p className="text-sm text-muted-foreground truncate" title={document.file_name}>
                {document.file_name}
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-2 flex-shrink-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8 hover:bg-muted"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onView?.(document)}>
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </DropdownMenuItem>
                
                <DropdownMenuItem 
                  onClick={handleDownload} 
                  disabled={downloadDocument.isPending || !canView}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </DropdownMenuItem>

                {canShare && (
                  <DropdownMenuItem onClick={handleShare}>
                    <Share2 className="h-4 w-4 mr-2" />
                    Share
                  </DropdownMenuItem>
                )}

                {canEdit && (
                  <DropdownMenuItem onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                )}

                {canManagePermissions && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleManagePermissions}>
                      <Shield className="h-4 w-4 mr-2" />
                      Manage Permissions
                    </DropdownMenuItem>
                  </>
                )}

                {canDelete && (
                  <>
                    <DropdownMenuSeparator />
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
        
        <div className="pt-2">
          {getStatusBadge()}
        </div>
      </CardHeader>
      
      <CardContent className="pt-0 space-y-4">
        <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          <div>
            <span className="text-muted-foreground">Size</span>
            <p className="font-medium">{formatFileSize(document.file_size)}</p>
          </div>
          
          <div>
            <span className="text-muted-foreground">Created</span>
            <p className="font-medium">{formatDate(document.created_at)}</p>
          </div>
          
          {document.expires_at && (
            <div>
              <span className="text-muted-foreground">Expires</span>
              <p className={`font-medium ${new Date(document.expires_at) < new Date() ? 'text-red-600 dark:text-red-400' : ''}`}>
                {formatDate(document.expires_at)}
              </p>
            </div>
          )}
          
          {document.view_limit && (
            <div>
              <span className="text-muted-foreground">Views</span>
              <p className="font-medium">
                {document.access_count} / {document.view_limit}
              </p>
            </div>
          )}
        </div>

        <div className="border-t pt-3">
          <div className="text-sm">
            <span className="text-muted-foreground block mb-1">
              {isOwner ? 'Recipient' : 'Sender'}
            </span>
            <p className="font-medium break-all text-foreground" title={isOwner ? document.recipient_email : document.sender_email}>
              {isOwner ? (document.recipient_email || 'Unknown') : (document.sender_email || 'Unknown')}
            </p>
          </div>
        </div>
        
        {document.description && (
          <div className="border-t pt-3">
            <span className="text-muted-foreground text-sm block mb-2">Description</span>
            <p className="text-sm text-foreground line-clamp-3" title={document.description}>
              {document.description}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}