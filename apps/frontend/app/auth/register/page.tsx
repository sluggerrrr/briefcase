'use client';

import { RegistrationForm } from '@/components/auth/RegistrationForm';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useEffect } from 'react';

export default function RegisterPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  // Redirect to dashboard if user is already logged in
  useEffect(() => {
    if (user && !isLoading) {
      router.push('/');
    }
  }, [user, isLoading, router]);

  const handleRegistrationSuccess = () => {
    router.push('/auth/login?message=Registration successful! Please log in.');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (user) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-md space-y-4">
        <RegistrationForm onSuccess={handleRegistrationSuccess} />
        
        <div className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link
            href="/auth/login"
            className="text-primary hover:underline font-medium"
          >
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  );
}