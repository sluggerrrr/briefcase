'use client';

import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { LogOut } from 'lucide-react';

interface LogoutButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}

export function LogoutButton({ variant = 'outline', size = 'default', className }: LogoutButtonProps) {
  const { logout } = useAuth();

  return (
    <Button
      variant={variant}
      size={size}
      className={className}
      onClick={logout}
    >
      <LogOut className="h-4 w-4 mr-2" />
      Sign out
    </Button>
  );
}