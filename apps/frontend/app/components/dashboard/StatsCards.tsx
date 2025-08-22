'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Shield, Upload } from 'lucide-react';

export function StatsCards() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5 text-blue-500" />
            Upload Documents
          </CardTitle>
          <CardDescription>
            Securely upload your files with encryption
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Drag and drop or browse to upload documents. All files are encrypted during upload.
          </p>
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
            <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Coming soon...</p>
          </div>
        </CardContent>
      </Card>

      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-green-500" />
            My Documents
          </CardTitle>
          <CardDescription>
            View and manage your uploaded files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Access your document library with advanced search and filtering.
          </p>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-2 bg-muted rounded">
              <span className="text-sm">No documents yet</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-purple-500" />
            Security Center
          </CardTitle>
          <CardDescription>
            Monitor access and security settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            View access logs and configure security preferences.
          </p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Encryption</span>
              <span className="text-green-500">Active</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Two-Factor Auth</span>
              <span className="text-muted-foreground">Coming soon</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}