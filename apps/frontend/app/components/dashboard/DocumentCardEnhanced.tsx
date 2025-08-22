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
import { 
  MoreVertical, 
  Download, 
  Eye, 
  Trash2, 
  Edit, 
  Share, 
  Settings, 
  Shield,
} from 'lucide-react';
import { toast } from 'sonner';

interface DocumentCardEnhancedProps {
  document: DocumentResponse;
  onEdit?: (document: DocumentResponse) => void;
  onView?: (document: DocumentResponse) => void;
  onShare?: (document: DocumentResponse) => void;
  onManagePermissions?: (document: DocumentResponse) => void;
}

export function DocumentCardEnhanced({ 
  document, 
  onEdit, 
  onView, 
  onShare, 
  onManagePermissions 
}: DocumentCardEnhancedProps) {
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
      toast.error('You do not have permission to manage document permissions');
      return;
    }
    onManagePermissions?.(document);
  };

  const getStatusBadge = () => {
    switch (document.status) {
      case 'active':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>;
      case 'expired':
        return <Badge variant="destructive">Expired</Badge>;
      case 'deleted':
        return <Badge variant="secondary" className="bg-gray-100 text-gray-800">Deleted</Badge>;
      default:
        return <Badge variant="outline">{document.status}</Badge>;
    }
  };

  const getPermissionBadges = () => {
    const permissionColors: Record<string, string> = {
      read: 'bg-blue-100 text-blue-800',
      write: 'bg-yellow-100 text-yellow-800',
      share: 'bg-purple-100 text-purple-800',
      delete: 'bg-red-100 text-red-800',
      admin: 'bg-gray-100 text-gray-800'
    };

    return permissions.map(permission => (
      <Badge 
        key={permission} 
        variant="secondary" 
        className={`text-xs ${permissionColors[permission] || 'bg-gray-100 text-gray-800'}`}
      >
        {permission}
      </Badge>
    ));
  };

  return (
    <Card 
      className={`hover:shadow-md transition-all cursor-pointer ${
        isSelected ? 'ring-2 ring-primary bg-primary/5' : ''
      } ${isSelectionMode ? 'hover:bg-muted/50' : ''}`}
      onClick={() => isSelectionMode && toggleDocumentSelection(document.id)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
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
            {isOwner && <Shield className="h-4 w-4 text-primary" title="Document Owner" />}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {canView && (
                  <DropdownMenuItem onClick={() => onView?.(document)}>
                    <Eye className="h-4 w-4 mr-2" />
                    View Details
                  </DropdownMenuItem>
                )}
                
                {canView && (
                  <DropdownMenuItem onClick={handleDownload} disabled={downloadDocument.isPending}>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </DropdownMenuItem>
                )}

                {canEdit && (
                  <DropdownMenuItem onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                )}

                {canShare && (
                  <DropdownMenuItem onClick={handleShare}>
                    <Share className="h-4 w-4 mr-2" />
                    Share
                  </DropdownMenuItem>
                )}

                {canManagePermissions && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleManagePermissions}>
                      <Settings className="h-4 w-4 mr-2" />
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
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Permission Badges */}
        {permissions.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {getPermissionBadges()}
          </div>
        )}

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

        {/* Quick Actions (only visible when not in selection mode) */}
        {!isSelectionMode && (
          <div className="flex gap-2 mt-3 pt-3 border-t">
            {canView && (
              <Button 
                size="sm" 
                variant="outline" 
                className="flex-1"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDownload();
                }}
              >
                <Download className="h-3 w-3 mr-1" />
                Download
              </Button>
            )}
            
            {canShare && (
              <Button 
                size="sm" 
                variant="outline" 
                className="flex-1"
                onClick={(e) => {
                  e.stopPropagation();
                  handleShare();
                }}
              >
                <Share className="h-3 w-3 mr-1" />
                Share
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}