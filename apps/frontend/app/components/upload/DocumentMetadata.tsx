'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText } from 'lucide-react';

interface DocumentMetadataProps {
  title: string;
  onTitleChange: (title: string) => void;
  description: string;
  onDescriptionChange: (description: string) => void;
  titleError?: string;
  descriptionError?: string;
  disabled?: boolean;
}

export function DocumentMetadata({
  title,
  onTitleChange,
  description,
  onDescriptionChange,
  titleError,
  descriptionError,
  disabled
}: DocumentMetadataProps) {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg">Document Information</CardTitle>
        </div>
        <CardDescription>
          Provide a title and description to help identify this document
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Title */}
        <div className="space-y-2">
          <Label htmlFor="title">
            Title <span className="text-destructive">*</span>
          </Label>
          <Input
            id="title"
            placeholder="Enter document title"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            disabled={disabled}
            maxLength={255}
            className={titleError ? 'border-destructive' : ''}
          />
          {titleError && (
            <p className="text-sm text-destructive">{titleError}</p>
          )}
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>A descriptive title helps identify the document</span>
            <span>{title.length}/255</span>
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            placeholder="Enter document description (optional)"
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            disabled={disabled}
            rows={3}
            maxLength={1000}
            className={`resize-none ${descriptionError ? 'border-destructive' : ''}`}
          />
          {descriptionError && (
            <p className="text-sm text-destructive">{descriptionError}</p>
          )}
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Additional context about the document content</span>
            <span>{description.length}/1000</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}