'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { FileDropZone } from './FileDropZone';
import { FilePreview } from './FilePreview';
import { RecipientSelector } from './RecipientSelector';
import { SecuritySettings } from './SecuritySettings';
import { DocumentMetadata } from './DocumentMetadata';
import { UploadProgress } from './UploadProgress';
import { useFileUpload } from '@/hooks/useFileUpload';
import { revokeFilePreview, type FileWithPreview } from '@/lib/upload-utils';
import { type User } from '@/hooks/useUserSearch';
import { Upload, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

interface DocumentUploadProps {
  onUploadComplete?: () => void;
  onCancel?: () => void;
}

export function DocumentUpload({ onUploadComplete, onCancel }: DocumentUploadProps) {
  const { uploadFile, getProgress, clearProgress } = useFileUpload();

  // Form state
  const [selectedFile, setSelectedFile] = useState<FileWithPreview | null>(null);
  const [recipient, setRecipient] = useState<User | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [expiresAt, setExpiresAt] = useState<Date | null>(null);
  const [viewLimit, setViewLimit] = useState<number | null>(null);

  // UI state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);

  // Form validation
  const [errors, setErrors] = useState<{
    file?: string;
    recipient?: string;
    title?: string;
  }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!selectedFile) {
      newErrors.file = 'Please select a file to upload';
    }

    if (!recipient) {
      newErrors.recipient = 'Please select a recipient';
    }

    if (!title.trim()) {
      newErrors.title = 'Please provide a document title';
    } else if (title.length > 255) {
      newErrors.title = 'Title must be less than 255 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFilesAdded = (files: FileWithPreview[]) => {
    if (files.length > 0) {
      // Clean up previous file preview
      if (selectedFile?.preview) {
        revokeFilePreview(selectedFile);
      }
      
      const file = files[0];
      setSelectedFile(file);
      
      // Auto-fill title from filename if empty
      if (!title.trim()) {
        const nameWithoutExtension = file.name.replace(/\.[^/.]+$/, '');
        setTitle(nameWithoutExtension);
      }
      
      // Clear file error
      setErrors(prev => ({ ...prev, file: undefined }));
    }
  };

  const handleFileRemove = () => {
    if (selectedFile?.preview) {
      revokeFilePreview(selectedFile);
    }
    setSelectedFile(null);
    setTitle('');
  };

  const handleUpload = async () => {
    if (!validateForm() || !selectedFile || !recipient) {
      return;
    }

    setIsUploading(true);

    try {
      const uploadData = {
        title: title.trim(),
        description: description.trim() || undefined,
        recipient_id: recipient.id,
        expires_at: expiresAt?.toISOString(),
        view_limit: viewLimit ?? undefined,
      };

      await uploadFile(selectedFile, uploadData);
      
      setUploadComplete(true);
      toast.success('Document uploaded successfully!');
      
      // Clean up file preview
      if (selectedFile.preview) {
        revokeFilePreview(selectedFile);
      }

      // Close modal after a short delay
      setTimeout(() => {
        onUploadComplete?.();
      }, 1500);
      
    } catch (error) {
      toast.error('Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCancel = () => {
    if (selectedFile?.preview) {
      revokeFilePreview(selectedFile);
    }
    clearProgress(selectedFile?.id || '');
    onCancel?.();
  };

  const progress = selectedFile ? getProgress(selectedFile.id) : undefined;

  if (uploadComplete) {
    return (
      <Card className="text-center">
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col items-center gap-4">
            <div className="p-3 rounded-full bg-green-100">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Upload Successful!</h3>
              <p className="text-muted-foreground mb-4">
                Your document &ldquo;{title}&rdquo; has been uploaded and shared with {recipient?.email}.
              </p>
              <p className="text-sm text-muted-foreground">
                The document list will refresh automatically.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column - File and Metadata */}
        <div className="space-y-6">
          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Select File</CardTitle>
              <CardDescription>
                Choose a document to upload and share
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!selectedFile ? (
                <div>
                  <FileDropZone onFilesAdded={handleFilesAdded} disabled={isUploading} />
                  {errors.file && (
                    <p className="text-sm text-destructive mt-2">{errors.file}</p>
                  )}
                </div>
              ) : (
                <FilePreview
                  file={selectedFile}
                  onRemove={handleFileRemove}
                  showProgress={isUploading}
                  progress={progress?.progress || 0}
                  status={progress?.status || 'preparing'}
                  error={progress?.error}
                  disabled={isUploading}
                />
              )}
            </CardContent>
          </Card>

          {/* Document Metadata */}
          {selectedFile && (
            <DocumentMetadata
              title={title}
              onTitleChange={setTitle}
              description={description}
              onDescriptionChange={setDescription}
              titleError={errors.title}
              disabled={isUploading}
            />
          )}
        </div>

        {/* Right Column - Recipient and Security */}
        <div className="space-y-6">
          {/* Recipient Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Recipient</CardTitle>
              <CardDescription>
                Select who will receive access to this document
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RecipientSelector
                selectedRecipient={recipient}
                onRecipientChange={setRecipient}
                error={errors.recipient}
                disabled={isUploading}
              />
            </CardContent>
          </Card>

          {/* Security Settings */}
          <SecuritySettings
            expiresAt={expiresAt}
            onExpiresAtChange={setExpiresAt}
            viewLimit={viewLimit}
            onViewLimitChange={setViewLimit}
            disabled={isUploading}
          />
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && selectedFile && progress && (
        <UploadProgress
          fileName={selectedFile.name}
          progress={progress.progress}
          status={progress.status}
          error={progress.error}
        />
      )}

      <Separator />

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <Button
          variant="outline"
          onClick={handleCancel}
          disabled={isUploading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleUpload}
          disabled={!selectedFile || !recipient || !title.trim() || isUploading}
        >
          <Upload className="h-4 w-4 mr-2" />
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </Button>
      </div>
    </div>
  );
}