'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { AppHeader } from '@/components/layout/AppHeader';
import { StatsCards } from './StatsCards';

export function DashboardLayout() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-background to-muted">
        <AppHeader />
        
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">Document Management Dashboard</h2>
              <p className="text-muted-foreground">
                Securely upload, manage, and share your documents
              </p>
            </div>

            <StatsCards />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}