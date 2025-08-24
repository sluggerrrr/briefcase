import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeClasses = {
  sm: 'h-6 w-6',
  md: 'h-8 w-8', 
  lg: 'h-10 w-10',
  xl: 'h-12 w-12'
};

const textSizeClasses = {
  sm: 'text-lg',
  md: 'text-xl',
  lg: 'text-2xl', 
  xl: 'text-3xl'
};

export function Logo({ className, showText = true, size = 'md' }: LogoProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Briefcase Icon SVG */}
      <svg 
        className={cn(sizeClasses[size], 'text-primary')}
        viewBox="0 0 24 24" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Briefcase body */}
        <rect
          x="3"
          y="8"
          width="18"
          height="11"
          rx="2"
          stroke="currentColor"
          strokeWidth="2"
          fill="currentColor"
          fillOpacity="0.1"
        />
        
        {/* Briefcase handle/top */}
        <path
          d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
          stroke="currentColor"
          strokeWidth="2"
          fill="none"
        />
        
        {/* Lock/security indicator */}
        <circle
          cx="12"
          cy="13"
          r="1.5"
          fill="currentColor"
        />
        
        {/* Security lines */}
        <path
          d="M10 13h4"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        
        {/* Document indicator */}
        <rect
          x="9"
          y="10"
          width="6"
          height="1"
          rx="0.5"
          fill="currentColor"
          fillOpacity="0.6"
        />
      </svg>
      
      {showText && (
        <span className={cn(
          'font-bold text-foreground tracking-tight',
          textSizeClasses[size]
        )}>
          Briefcase
        </span>
      )}
    </div>
  );
}

export function LogoIcon({ className, size = 'md' }: Omit<LogoProps, 'showText'>) {
  return <Logo className={className} size={size} showText={false} />;
}