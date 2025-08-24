'use client';

import { cn } from '@/lib/utils';

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'default' | 'card' | 'text' | 'circle' | 'document';
  lines?: number;
  animated?: boolean;
}

export function LoadingSkeleton({ 
  className, 
  variant = 'default',
  lines = 1,
  animated = true
}: LoadingSkeletonProps) {
  const baseClasses = cn(
    'bg-muted rounded-md',
    animated && 'animate-pulse',
    className
  );

  if (variant === 'card') {
    return (
      <div className={cn('space-y-3 p-4 border rounded-lg', className)}>
        <div className="flex items-center space-x-4">
          <div className="rounded-full bg-muted h-12 w-12 animate-pulse" />
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-muted rounded animate-pulse" />
            <div className="h-4 bg-muted rounded w-3/4 animate-pulse" />
          </div>
        </div>
        <div className="space-y-2">
          <div className="h-3 bg-muted rounded animate-pulse" />
          <div className="h-3 bg-muted rounded w-5/6 animate-pulse" />
          <div className="h-3 bg-muted rounded w-4/6 animate-pulse" />
        </div>
      </div>
    );
  }

  if (variant === 'document') {
    return (
      <div className={cn('space-y-3 p-4 border rounded-lg', className)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-muted rounded animate-pulse" />
            <div className="space-y-1">
              <div className="h-4 w-32 bg-muted rounded animate-pulse" />
              <div className="h-3 w-24 bg-muted rounded animate-pulse" />
            </div>
          </div>
          <div className="h-8 w-20 bg-muted rounded animate-pulse" />
        </div>
        <div className="space-y-2">
          <div className="h-3 bg-muted rounded w-3/4 animate-pulse" />
          <div className="h-3 bg-muted rounded w-1/2 animate-pulse" />
        </div>
      </div>
    );
  }

  if (variant === 'circle') {
    return <div className={cn('rounded-full bg-muted h-12 w-12', animated && 'animate-pulse', className)} />;
  }

  if (variant === 'text') {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }, (_, i) => (
          <div 
            key={i} 
            className={cn(
              'h-4 bg-muted rounded',
              i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full',
              animated && 'animate-pulse'
            )} 
          />
        ))}
      </div>
    );
  }

  // Default skeleton
  return <div className={baseClasses} />;
}

// Specific skeleton components for common use cases
export function DocumentCardSkeleton({ className }: { className?: string }) {
  return <LoadingSkeleton variant="document" className={className} />;
}

export function UserProfileSkeleton({ className }: { className?: string }) {
  return <LoadingSkeleton variant="card" className={className} />;
}

export function TextSkeleton({ 
  lines = 3, 
  className 
}: { 
  lines?: number; 
  className?: string; 
}) {
  return <LoadingSkeleton variant="text" lines={lines} className={className} />;
}