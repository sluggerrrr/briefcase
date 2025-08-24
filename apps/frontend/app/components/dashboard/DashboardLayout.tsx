'use client';

import { useState } from 'react';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { AppHeader } from '../layout/AppHeader';
import { DocumentList } from './DocumentList';
import { DocumentUpload } from '../upload/DocumentUpload';
import { DocumentSelectionProvider } from '@/contexts/DocumentSelectionContext';
import { PermissionProvider } from '@/contexts/PermissionContext';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Upload } from 'lucide-react';
import { Toaster } from 'sonner';

export function DashboardLayout() {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  const handleUploadComplete = () => {
    setUploadDialogOpen(false);
    // DocumentList will automatically refresh due to TanStack Query invalidation
  };

  const handleUploadCancel = () => {
    setUploadDialogOpen(false);
  };

  return (
    <ProtectedRoute>
      <PermissionProvider>
        <DocumentSelectionProvider>
          <div className="min-h-screen bg-gradient-to-br from-background to-muted">
          <AppHeader />
          
          <main className="container mx-auto px-4 py-8">
            <div className="max-w-7xl mx-auto">
              <div className="mb-8">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Document Management Dashboard</h2>
                    <p className="text-muted-foreground">
                      Securely upload, manage, and share your documents
                    </p>
                  </div>
                  <Button 
                    className="gap-2"
                    onClick={() => setUploadDialogOpen(true)}
                  >
                    <Upload className="h-4 w-4" />
                    Upload Document
                  </Button>
                </div>
              </div>

              <DocumentList />
            </div>
          </main>

        {/* Upload Modal */}
        <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
          <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload Document
              </DialogTitle>
            </DialogHeader>
            <DocumentUpload 
              onUploadComplete={handleUploadComplete}
              onCancel={handleUploadCancel}
            />
          </DialogContent>
        </Dialog>
        
            <Toaster position="top-right" />
          </div>
        </DocumentSelectionProvider>
      </PermissionProvider>
    </ProtectedRoute>
  );
}