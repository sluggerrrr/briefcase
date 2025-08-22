'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Trash2, 
  Share, 
  Download, 
  X, 
  MoreHorizontal,
  Users,
  Settings
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useDocumentSelection } from '@/contexts/DocumentSelectionContext';
import { useBulkOperationPermissions } from '@/contexts/PermissionContext';
import { BulkDeleteDialog } from './BulkDeleteDialog';
import { BulkShareDialog } from './BulkShareDialog';
import { useBulkOperations } from '@/hooks/useBulkOperations';
import { toast } from 'sonner';

interface BulkActionsToolbarProps {
  totalDocuments: number;
  onSelectAll: () => void;
  className?: string;
}

export function BulkActionsToolbar({ 
  totalDocuments, 
  onSelectAll, 
  className 
}: BulkActionsToolbarProps) {
  const { 
    selectedCount, 
    clearSelection, 
    setSelectionMode,
    getSelectedDocumentIds 
  } = useDocumentSelection();
  
  const selectedDocumentIds = getSelectedDocumentIds();
  const {
    canBulkView,
    canBulkShare,
    canBulkDelete,
    canBulkManage
  } = useBulkOperationPermissions(selectedDocumentIds);

  const { bulkDownload } = useBulkOperations();

  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);

  const handleClearSelection = () => {
    clearSelection();
    setSelectionMode(false);
  };

  const handleBulkDownload = async () => {
    if (!canBulkView) {
      toast.error('You do not have permission to download some selected documents');
      return;
    }

    try {
      await bulkDownload(selectedDocumentIds);
      toast.success(`Downloading ${selectedCount} documents...`);
    } catch (error) {
      toast.error('Failed to download documents');
      console.error('Bulk download error:', error);
    }
  };

  return (
    <div className={`flex items-center justify-between bg-muted/50 p-4 rounded-lg border ${className}`}>
      {/* Selection Info */}
      <div className="flex items-center gap-3">
        <Badge variant="secondary" className="text-sm">
          {selectedCount} selected
        </Badge>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={onSelectAll}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          Select all {totalDocuments}
        </Button>
        
        <Separator orientation="vertical" className="h-4" />
        
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClearSelection}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          <X className="h-3 w-3 mr-1" />
          Clear selection
        </Button>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        {/* Download */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleBulkDownload}
          disabled={!canBulkView || selectedCount === 0}
          className="gap-2"
        >
          <Download className="h-4 w-4" />
          Download
        </Button>

        {/* Share */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowShareDialog(true)}
          disabled={!canBulkShare || selectedCount === 0}
          className="gap-2"
        >
          <Share className="h-4 w-4" />
          Share
        </Button>

        {/* Delete */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowDeleteDialog(true)}
          disabled={!canBulkDelete || selectedCount === 0}
          className="gap-2 text-destructive hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
          Delete
        </Button>

        {/* More Actions */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              disabled={selectedCount === 0}
              className="gap-2"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              disabled={!canBulkShare}
              onClick={() => setShowShareDialog(true)}
            >
              <Users className="h-4 w-4 mr-2" />
              Bulk Share
            </DropdownMenuItem>
            
            {canBulkManage && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled={!canBulkManage}>
                  <Settings className="h-4 w-4 mr-2" />
                  Manage Permissions
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Dialogs */}
      <BulkDeleteDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        documentIds={selectedDocumentIds}
        documentCount={selectedCount}
      />

      <BulkShareDialog
        open={showShareDialog}
        onOpenChange={setShowShareDialog}
        documentIds={selectedDocumentIds}
        documentCount={selectedCount}
      />
    </div>
  );
}