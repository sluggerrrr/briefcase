'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DocumentResponse } from '@/lib/documents';
import { useUpdateDocument } from '@/hooks/useDocuments';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

interface EditDocumentDialogProps {
  document: DocumentResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditDocumentDialog({ document, open, onOpenChange }: EditDocumentDialogProps) {
  const [title, setTitle] = useState(document.title);
  const [description, setDescription] = useState(document.description || '');
  const [viewLimit, setViewLimit] = useState<number | undefined>(document.view_limit || undefined);
  const [expiresIn, setExpiresIn] = useState<string>('');

  const updateDocument = useUpdateDocument();

  useEffect(() => {
    if (open) {
      setTitle(document.title);
      setDescription(document.description || '');
      setViewLimit(document.view_limit || undefined);
      
      // Calculate expires in days if document has expiration
      if (document.expires_at) {
        const expiresAt = new Date(document.expires_at);
        const now = new Date();
        const diffDays = Math.ceil((expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        setExpiresIn(diffDays > 0 ? diffDays.toString() : 'none');
      } else {
        setExpiresIn('none');
      }
    }
  }, [open, document]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const updateData: any = {
      title: title.trim(),
      description: description.trim() || null,
      view_limit: viewLimit || null,
    };

    // Calculate new expiration date if expires_in is provided
    if (expiresIn && expiresIn !== 'none' && parseInt(expiresIn) > 0) {
      const expirationDate = new Date();
      expirationDate.setDate(expirationDate.getDate() + parseInt(expiresIn));
      updateData.expires_at = expirationDate.toISOString();
    } else if (expiresIn === 'none' || expiresIn === '') {
      // Remove expiration if "none" is selected or field is empty
      updateData.expires_at = null;
    }

    try {
      await updateDocument.mutateAsync({
        id: document.id,
        data: updateData
      });
      
      toast.success('Document updated successfully');
      onOpenChange(false);
    } catch (error) {
      toast.error('Failed to update document');
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Edit Document</DialogTitle>
          <DialogDescription>
            Update document settings and metadata
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Document Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter document title"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter document description"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="viewLimit">View Limit (Optional)</Label>
              <Input
                id="viewLimit"
                type="number"
                min="1"
                value={viewLimit || ''}
                onChange={(e) => setViewLimit(e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="Maximum number of views"
              />
            </div>

            <div>
              <Label htmlFor="expiresIn">Expires In (Days)</Label>
              <Select value={expiresIn} onValueChange={setExpiresIn}>
                <SelectTrigger>
                  <SelectValue placeholder="Select expiration" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">No expiration</SelectItem>
                  <SelectItem value="1">1 day</SelectItem>
                  <SelectItem value="7">1 week</SelectItem>
                  <SelectItem value="30">1 month</SelectItem>
                  <SelectItem value="90">3 months</SelectItem>
                  <SelectItem value="365">1 year</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={updateDocument.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateDocument.isPending || !title.trim()}
            >
              {updateDocument.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Update Document
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}