'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { RecipientSelector } from '@/components/upload/RecipientSelector';
import { SecuritySettings } from '@/components/upload/SecuritySettings';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { type DocumentResponse } from '@/lib/documents';
import { type User } from '@/hooks/useUserSearch';
import { Share2, FileText } from 'lucide-react';
import { toast } from 'sonner';

interface ShareDocumentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  document: DocumentResponse | null;
}

export function ShareDocumentDialog({ open, onOpenChange, document }: ShareDocumentDialogProps) {
  const [recipient, setRecipient] = useState<User | null>(null);
  const [expiresAt, setExpiresAt] = useState<Date | null>(null);
  const [viewLimit, setViewLimit] = useState<number | null>(null);
  const [isSharing, setIsSharing] = useState(false);

  const [errors, setErrors] = useState<{
    recipient?: string;
  }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!recipient) {
      newErrors.recipient = 'Please select a recipient';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleShare = async () => {
    if (!document || !validateForm() || !recipient) {
      return;
    }

    setIsSharing(true);

    try {
      // TODO: Implement document sharing API call
      // For now, just simulate the API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success(`Document "${document.title}" shared successfully with ${recipient.name}!`);
      
      // Reset form and close dialog
      setRecipient(null);
      setExpiresAt(null);
      setViewLimit(null);
      setErrors({});
      onOpenChange(false);
      
    } catch (error) {
      toast.error('Failed to share document. Please try again.');
      console.error('Share error:', error);
    } finally {
      setIsSharing(false);
    }
  };

  const handleCancel = () => {
    setRecipient(null);
    setExpiresAt(null);
    setViewLimit(null);
    setErrors({});
    onOpenChange(false);
  };

  if (!document) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            Share Document
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Document Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Document to Share</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-md bg-primary/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm truncate" title={document.title}>
                    {document.title}
                  </h4>
                  <p className="text-xs text-muted-foreground truncate">
                    {document.file_name} • Created {new Date(document.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Recipient Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Recipient</CardTitle>
                <CardDescription>
                  Select who will receive access to this document
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RecipientSelector
                  selectedRecipient={recipient}
                  onRecipientChange={setRecipient}
                  error={errors.recipient}
                  disabled={isSharing}
                />
              </CardContent>
            </Card>

            {/* Security Settings */}
            <div>
              <SecuritySettings
                expiresAt={expiresAt}
                onExpiresAtChange={setExpiresAt}
                viewLimit={viewLimit}
                onViewLimitChange={setViewLimit}
                disabled={isSharing}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={isSharing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleShare}
              disabled={!recipient || isSharing}
            >
              <Share2 className="h-4 w-4 mr-2" />
              {isSharing ? 'Sharing...' : 'Share Document'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}