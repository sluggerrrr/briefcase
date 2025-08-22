'use client';

import { useCallback, useState } from 'react';
import { Button } from '@/components/ui/button';
import { validateFile, processFileForUpload, type FileWithPreview } from '@/lib/upload-utils';
import { Upload, File, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

interface FileDropZoneProps {
  onFilesAdded: (files: FileWithPreview[]) => void;
  maxFiles?: number;
  className?: string;
  disabled?: boolean;
}

export function FileDropZone({ onFilesAdded, maxFiles = 1, className, disabled }: FileDropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFiles = useCallback((fileList: FileList) => {
    const files = Array.from(fileList);
    
    // Check max files limit
    if (files.length > maxFiles) {
      toast.error(`You can only upload up to ${maxFiles} file${maxFiles > 1 ? 's' : ''} at a time`);
      return;
    }

    const validFiles: FileWithPreview[] = [];
    const errors: string[] = [];

    files.forEach(file => {
      const validation = validateFile(file);
      if (validation.isValid) {
        validFiles.push(processFileForUpload(file));
      } else {
        errors.push(`${file.name}: ${validation.error}`);
      }
    });

    // Show validation errors
    if (errors.length > 0) {
      errors.forEach(error => toast.error(error));
    }

    // Add valid files
    if (validFiles.length > 0) {
      onFilesAdded(validFiles);
    }
  }, [onFilesAdded, maxFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles, disabled]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
    // Reset input value to allow selecting the same file again
    e.target.value = '';
  }, [handleFiles]);

  const handleClick = () => {
    if (disabled) return;
    document.getElementById('file-input')?.click();
  };

  return (
    <div className={className}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragOver && !disabled
            ? 'border-primary bg-primary/5 scale-[1.02]'
            : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          id="file-input"
          type="file"
          multiple={maxFiles > 1}
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
          disabled={disabled}
          accept={[
            '.pdf',
            '.doc', '.docx',
            '.xls', '.xlsx',
            '.ppt', '.pptx',
            '.txt', '.csv',
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
            '.zip', '.rar', '.7z'
          ].join(',')}
        />

        <div className="flex flex-col items-center gap-4">
          {isDragOver && !disabled ? (
            <>
              <div className="p-3 rounded-full bg-primary/10">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-lg font-medium text-primary">Drop files here</p>
                <p className="text-sm text-muted-foreground">Release to upload</p>
              </div>
            </>
          ) : (
            <>
              <div className="p-3 rounded-full bg-muted">
                <File className="h-8 w-8 text-muted-foreground" />
              </div>
              <div>
                <p className="text-lg font-medium mb-1">
                  Drag and drop {maxFiles > 1 ? 'files' : 'a file'} here
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  or click to browse your files
                </p>
                <Button variant="outline" size="sm" disabled={disabled}>
                  <Upload className="h-4 w-4 mr-2" />
                  Choose {maxFiles > 1 ? 'Files' : 'File'}
                </Button>
              </div>
            </>
          )}
        </div>

        <div className="mt-6 text-xs text-muted-foreground">
          <div className="flex items-center justify-center gap-1 mb-2">
            <AlertCircle className="h-3 w-3" />
            <span>Supported formats</span>
          </div>
          <p>
            Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV
          </p>
          <p>
            Images: JPG, PNG, GIF, WebP, SVG
          </p>
          <p>
            Archives: ZIP, RAR, 7Z
          </p>
          <p className="mt-2 font-medium">
            Maximum file size: 10MB
          </p>
        </div>
      </div>
    </div>
  );
}