'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatFileSize, getFileIcon, getFileCategory, type FileWithPreview } from '@/lib/upload-utils';
import { X, FileText, Image as ImageIcon, Archive } from 'lucide-react';

interface FilePreviewProps {
  file: FileWithPreview;
  onRemove: () => void;
  showProgress?: boolean;
  progress?: number;
  status?: 'preparing' | 'uploading' | 'completed' | 'error';
  error?: string;
  disabled?: boolean;
}

export function FilePreview({ 
  file, 
  onRemove, 
  showProgress = false, 
  progress = 0, 
  status = 'preparing',
  error,
  disabled 
}: FilePreviewProps) {
  const category = getFileCategory(file.name);
  
  const getCategoryIcon = () => {
    switch (category) {
      case 'document':
        return <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />;
      case 'image':
        return <ImageIcon className="h-5 w-5 text-green-600 dark:text-green-400" />;
      case 'archive':
        return <Archive className="h-5 w-5 text-purple-600 dark:text-purple-400" />;
      default:
        return <FileText className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getCategoryColor = () => {
    switch (category) {
      case 'document':
        return 'bg-blue-500/10 border-blue-500/20';
      case 'image':
        return 'bg-green-500/10 border-green-500/20';
      case 'archive':
        return 'bg-purple-500/10 border-purple-500/20';
      default:
        return 'bg-muted/50 border-border';
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'preparing':
        return <Badge variant="secondary">Preparing...</Badge>;
      case 'uploading':
        return <Badge variant="secondary">Uploading...</Badge>;
      case 'completed':
        return <Badge variant="default" className="bg-green-500">Completed</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return null;
    }
  };

  return (
    <Card className={`relative ${getCategoryColor()}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* File icon or image preview */}
          <div className="flex-shrink-0">
            {file.preview ? (
              <div className="w-12 h-12 rounded-md overflow-hidden border">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={file.preview} 
                  alt={`Preview of ${file.name}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ) : (
              <div className="w-12 h-12 rounded-md border bg-background flex items-center justify-center">
                {getCategoryIcon()}
              </div>
            )}
          </div>

          {/* File details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <h4 className="font-medium text-sm truncate" title={file.name}>
                {file.name}
              </h4>
              {!disabled && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 hover:bg-destructive/10 hover:text-destructive"
                  onClick={onRemove}
                >
                  <X className="h-3 w-3" />
                </Button>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
              <span>{formatFileSize(file.size)}</span>
              <span>•</span>
              <span className="capitalize">{category}</span>
              <span>•</span>
              <span>{file.type}</span>
            </div>

            {/* Progress bar */}
            {showProgress && (
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  {getStatusBadge()}
                  {status === 'uploading' && (
                    <span className="text-xs text-muted-foreground">{Math.round(progress)}%</span>
                  )}
                </div>
                
                {(status === 'preparing' || status === 'uploading') && (
                  <div className="w-full bg-muted rounded-full h-1.5">
                    <div 
                      className="bg-primary h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                )}

                {error && (
                  <p className="text-xs text-destructive mt-1">{error}</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* File icon emoji as decoration */}
        <div className="absolute top-2 right-2 text-lg opacity-20">
          {getFileIcon(file.name)}
        </div>
      </CardContent>
    </Card>
  );
}