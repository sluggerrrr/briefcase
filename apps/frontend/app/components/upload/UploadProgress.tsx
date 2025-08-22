'use client';

import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Upload, Loader2 } from 'lucide-react';

interface UploadProgressProps {
  fileName: string;
  progress: number;
  status: 'preparing' | 'uploading' | 'completed' | 'error';
  error?: string;
}

export function UploadProgress({ fileName, progress, status, error }: UploadProgressProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'preparing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'uploading':
        return <Upload className="h-4 w-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
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
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return null;
    }
  };

  const getProgressColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return '';
    }
  };

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              {getStatusIcon()}
              <span className="font-medium text-sm truncate" title={fileName}>
                {fileName}
              </span>
            </div>
            {getStatusBadge()}
          </div>

          {/* Progress Bar */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                {status === 'preparing' && 'Preparing file...'}
                {status === 'uploading' && 'Uploading...'}
                {status === 'completed' && 'Upload complete'}
                {status === 'error' && 'Upload failed'}
              </span>
              {(status === 'uploading' || status === 'preparing') && (
                <span>{Math.round(progress)}%</span>
              )}
            </div>
            <Progress 
              value={progress} 
              className={`h-2 ${getProgressColor()}`}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="text-sm text-destructive bg-destructive/5 p-2 rounded border border-destructive/20">
              {error}
            </div>
          )}

          {/* Success Message */}
          {status === 'completed' && (
            <div className="text-sm text-green-600 bg-green-50 p-2 rounded border border-green-200">
              Document uploaded successfully!
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}