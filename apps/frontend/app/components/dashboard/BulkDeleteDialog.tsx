'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Trash2, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { useBulkOperations } from '@/hooks/useBulkOperations';
import { useDocumentSelection } from '@/contexts/DocumentSelectionContext';
import { toast } from 'sonner';

interface BulkDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentIds: string[];
  documentCount: number;
}

interface DeleteResult {
  documentId: string;
  status: 'pending' | 'success' | 'failed' | 'permission_denied';
  error?: string;
}

interface BulkOperationResult {
  document_id: string;
  status: 'success' | 'failed' | 'permission_denied';
  error?: string;
}

export function BulkDeleteDialog({
  open,
  onOpenChange,
  documentIds,
  documentCount
}: BulkDeleteDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteResults, setDeleteResults] = useState<DeleteResult[]>([]);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const { bulkDelete } = useBulkOperations();
  const { clearSelection } = useDocumentSelection();

  const handleDelete = async () => {
    if (!confirmDelete) return;

    setIsDeleting(true);
    setShowResults(true);

    // Initialize results
    const initialResults: DeleteResult[] = documentIds.map(id => ({
      documentId: id,
      status: 'pending'
    }));
    setDeleteResults(initialResults);

    try {
      const result = await bulkDelete(documentIds);
      
      // Update results based on API response
      const updatedResults = result.results.map((apiResult: BulkOperationResult) => ({
        documentId: apiResult.document_id,
        status: apiResult.status,
        error: apiResult.error
      }));
      
      setDeleteResults(updatedResults);

      // Show summary toast
      if (result.successful > 0) {
        toast.success(`Successfully deleted ${result.successful} document${result.successful > 1 ? 's' : ''}`);
      }
      
      if (result.failed > 0) {
        toast.error(`Failed to delete ${result.failed} document${result.failed > 1 ? 's' : ''}`);
      }

      // Clear selection for successfully deleted documents
      const successfulIds = updatedResults
        .filter(r => r.status === 'success')
        .map(r => r.documentId);
      
      if (successfulIds.length > 0) {
        clearSelection();
      }

    } catch (error) {
      console.error('Bulk delete error:', error);
      toast.error('Failed to delete documents');
      
      // Mark all as failed
      setDeleteResults(prev =>
        prev.map(result => ({
          ...result,
          status: 'failed',
          error: 'Network error'
        }))
      );
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    if (isDeleting) return; // Prevent closing during operation
    
    setConfirmDelete(false);
    setShowResults(false);
    setDeleteResults([]);
    onOpenChange(false);
  };

  const getResultIcon = (status: DeleteResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
      case 'permission_denied':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-muted animate-spin" />;
    }
  };

  const getResultText = (result: DeleteResult) => {
    switch (result.status) {
      case 'success':
        return 'Deleted successfully';
      case 'permission_denied':
        return 'Permission denied';
      case 'failed':
        return result.error || 'Delete failed';
      default:
        return 'Deleting...';
    }
  };

  const completedCount = deleteResults.filter(r => r.status !== 'pending').length;
  const progressPercentage = documentCount > 0 ? (completedCount / documentCount) * 100 : 0;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-destructive" />
            Delete Documents
          </DialogTitle>
          <DialogDescription>
            {showResults ? (
              `Deleting ${documentCount} document${documentCount > 1 ? 's' : ''}...`
            ) : (
              `You are about to delete ${documentCount} document${documentCount > 1 ? 's' : ''}. This action cannot be undone.`
            )}
          </DialogDescription>
        </DialogHeader>

        {showResults ? (
          <div className="space-y-4">
            {/* Progress */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{completedCount} of {documentCount}</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>

            {/* Results List */}
            <ScrollArea className="max-h-48">
              <div className="space-y-2">
                {deleteResults.map((result) => (
                  <div
                    key={result.documentId}
                    className="flex items-center justify-between p-2 rounded-md bg-muted/50"
                  >
                    <div className="flex items-center gap-2">
                      {getResultIcon(result.status)}
                      <span className="text-sm font-mono text-muted-foreground">
                        {result.documentId.slice(0, 8)}...
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {getResultText(result)}
                    </span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Warning */}
            <div className="flex items-start gap-3 p-3 rounded-md bg-destructive/10 border border-destructive/20">
              <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-destructive mb-1">Warning</p>
                <p className="text-destructive/80">
                  This will permanently delete the selected documents. 
                  You will not be able to recover them.
                </p>
              </div>
            </div>

            {/* Confirmation */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="confirm-delete"
                checked={confirmDelete}
                onCheckedChange={(checked) => setConfirmDelete(checked as boolean)}
              />
              <label
                htmlFor="confirm-delete"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                I understand this action cannot be undone
              </label>
            </div>
          </div>
        )}

        <DialogFooter>
          {showResults ? (
            <Button
              onClick={handleClose}
              disabled={isDeleting}
              className="w-full"
            >
              {isDeleting ? 'Deleting...' : 'Close'}
            </Button>
          ) : (
            <div className="flex gap-2 w-full">
              <Button
                variant="outline"
                onClick={handleClose}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={!confirmDelete}
                className="flex-1"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete {documentCount}
              </Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}