'use client';

import { useMemo } from 'react';
import { cn } from '@/lib/utils';

interface PasswordStrengthIndicatorProps {
  password: string;
  className?: string;
}

interface PasswordStrength {
  score: number; // 0-4
  label: string;
  feedback: string[];
  color: string;
}

export function PasswordStrengthIndicator({ password, className }: PasswordStrengthIndicatorProps) {
  const strength = useMemo(() => calculatePasswordStrength(password), [password]);

  if (!password) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)} aria-label="Password strength indicator">
      {/* Strength Meter */}
      <div className="flex space-x-1">
        {[...Array(4)].map((_, index) => (
          <div
            key={index}
            className={cn(
              'h-1.5 flex-1 rounded-full transition-colors',
              index < strength.score
                ? strength.color
                : 'bg-muted'
            )}
          />
        ))}
      </div>
      
      {/* Strength Label */}
      <div className="flex items-center justify-between text-xs">
        <span className={cn('font-medium', 
          strength.score < 2 ? 'text-destructive' :
          strength.score < 3 ? 'text-yellow-600' :
          'text-green-600'
        )}>
          {strength.label}
        </span>
        <span className="text-muted-foreground">
          {password.length} characters
        </span>
      </div>

      {/* Feedback */}
      {strength.feedback.length > 0 && (
        <ul className="text-xs text-muted-foreground space-y-1" role="list">
          {strength.feedback.map((feedback, index) => (
            <li key={index} className="flex items-center gap-1">
              <span className="text-yellow-600">•</span>
              {feedback}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function calculatePasswordStrength(password: string): PasswordStrength {
  const feedback: string[] = [];
  let score = 0;

  if (password.length < 6) {
    feedback.push('Use at least 6 characters');
  } else {
    score += 1;
  }

  if (password.length >= 8) {
    score += 1;
  } else if (password.length >= 6) {
    feedback.push('Consider using 8+ characters');
  }

  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSymbol = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  if (hasLower && hasUpper) {
    score += 1;
  } else {
    feedback.push('Mix uppercase and lowercase letters');
  }

  if (hasNumber) {
    score += 0.5;
  } else {
    feedback.push('Include numbers');
  }

  if (hasSymbol) {
    score += 0.5;
  } else {
    feedback.push('Add special characters (!@#$...)');
  }

  // Round score to nearest integer, max 4
  score = Math.min(4, Math.round(score));

  let label: string;
  let color: string;

  switch (score) {
    case 0:
    case 1:
      label = 'Weak';
      color = 'bg-destructive';
      break;
    case 2:
      label = 'Fair';
      color = 'bg-yellow-500';
      break;
    case 3:
      label = 'Good';
      color = 'bg-yellow-400';
      break;
    case 4:
      label = 'Strong';
      color = 'bg-green-500';
      break;
    default:
      label = 'Unknown';
      color = 'bg-muted';
  }

  return {
    score,
    label,
    feedback,
    color
  };
}