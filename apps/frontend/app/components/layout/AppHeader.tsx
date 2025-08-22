'use client';

import { LogoutButton } from '@/components/auth/LogoutButton';
import { useAuth } from '@/hooks/useAuth';
import { Shield } from 'lucide-react';
import Link from 'next/link';

export function AppHeader() {
  const { user } = useAuth();

  return (
    <header className="border-b bg-background/80 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="flex items-center gap-2 hover:opacity-90">
          <Shield className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold">Briefcase</h1>
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            Welcome, {user?.name || user?.email}
          </span>
          <LogoutButton />
        </div>
      </div>
    </header>
  );
}