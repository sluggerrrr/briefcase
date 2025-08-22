export interface FileValidationResult {
  isValid: boolean;
  error?: string;
}

export interface FileWithPreview extends File {
  id: string;
  preview?: string;
}

// Allowed MIME types for uploads
export const ALLOWED_MIME_TYPES = [
  // Documents
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/csv',
  // Images
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',
  // Archives
  'application/zip',
  'application/x-zip-compressed',
  'application/x-rar-compressed',
  'application/x-7z-compressed',
];

// File type categories for display
export const FILE_TYPE_CATEGORIES = {
  document: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'],
  image: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
  archive: ['zip', 'rar', '7z'],
};

// Maximum file size in bytes (10MB)
export const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Maximum base64 string length (roughly 14MB for 10MB file)
export const MAX_BASE64_SIZE = 14 * 1024 * 1024;

/**
 * Validate a file for upload
 */
export function validateFile(file: File): FileValidationResult {
  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: `File size must be less than ${formatFileSize(MAX_FILE_SIZE)}`,
    };
  }

  // Check MIME type
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    return {
      isValid: false,
      error: `File type "${file.type}" is not supported`,
    };
  }

  // Check file name
  if (file.name.length > 255) {
    return {
      isValid: false,
      error: 'File name must be less than 255 characters',
    };
  }

  // Check for suspicious file extensions
  const suspiciousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com'];
  const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  if (suspiciousExtensions.includes(extension)) {
    return {
      isValid: false,
      error: 'This file type is not allowed for security reasons',
    };
  }

  return { isValid: true };
}

/**
 * Convert file to base64 string
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        // Remove data URL prefix (e.g., "data:image/png;base64,")
        const base64 = reader.result.split(',')[1];
        
        // Validate base64 size
        if (base64.length > MAX_BASE64_SIZE) {
          reject(new Error('File is too large after encoding'));
          return;
        }
        
        resolve(base64);
      } else {
        reject(new Error('Failed to read file'));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    
    reader.readAsDataURL(file);
  });
}

/**
 * Create a preview URL for image files
 */
export function createImagePreview(file: File): string | null {
  if (file.type.startsWith('image/')) {
    return URL.createObjectURL(file);
  }
  return null;
}

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  return filename.substring(filename.lastIndexOf('.') + 1).toLowerCase();
}

/**
 * Get file category based on extension
 */
export function getFileCategory(filename: string): string {
  const extension = getFileExtension(filename);
  
  for (const [category, extensions] of Object.entries(FILE_TYPE_CATEGORIES)) {
    if (extensions.includes(extension)) {
      return category;
    }
  }
  
  return 'other';
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * Get appropriate icon for file type
 */
export function getFileIcon(filename: string): string {
  const category = getFileCategory(filename);
  
  switch (category) {
    case 'document':
      return '📄';
    case 'image':
      return '🖼️';
    case 'archive':
      return '🗜️';
    default:
      return '📎';
  }
}

/**
 * Generate unique ID for file
 */
export function generateFileId(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

/**
 * Add ID and preview to file
 */
export function processFileForUpload(file: File): FileWithPreview {
  const fileWithId = Object.assign(file, { id: generateFileId() });
  const preview = createImagePreview(file);
  
  return Object.assign(fileWithId, { preview: preview || undefined });
}

/**
 * Clean up preview URLs
 */
export function revokeFilePreview(file: FileWithPreview): void {
  if (file.preview) {
    URL.revokeObjectURL(file.preview);
  }
}