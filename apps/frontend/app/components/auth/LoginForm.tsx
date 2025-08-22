'use client';

import { useForm } from '@tanstack/react-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/useAuth';
import { useState } from 'react';
import { Eye, EyeOff, Lock, Mail } from 'lucide-react';
import type { LoginCredentials } from '@/lib/auth';

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const { login, loginAsync, isLoggingIn, loginError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm({
    defaultValues: {
      email: '',
      password: '',
    },
    onSubmit: async ({ value }: { value: LoginCredentials }) => {
      try {
        await (loginAsync ? loginAsync(value) : Promise.resolve(login(value)));
        onSuccess?.();
      } catch (error) {
        console.error('Form submission error:', error);
      }
    },
  });

  const validateEmail = ({ value }: { value: string }) => {
    if (!value) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
    return undefined;
  };

  const validatePassword = ({ value }: { value: string }) => {
    if (!value) return 'Password is required';
    if (value.length < 6) return 'Password must be at least 6 characters';
    return undefined;
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold">Welcome to Briefcase</CardTitle>
        <CardDescription>
          Enter your credentials to access your secure documents
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="space-y-4"
        >
          <form.Field
            name="email"
            validators={{
              onChange: validateEmail,
              onBlur: validateEmail,
              onSubmit: validateEmail,
            }}
          >
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id={field.name}
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    disabled={isLoggingIn}
                  />
                </div>
                {field.state.meta.errors?.length ? (
                  <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                ) : null}
              </div>
            )}
          </form.Field>

          <form.Field
            name="password"
            validators={{
              onChange: validatePassword,
              onBlur: validatePassword,
              onSubmit: validatePassword,
            }}
          >
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id={field.name}
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    className="pl-10 pr-10"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    disabled={isLoggingIn}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoggingIn}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </div>
                {field.state.meta.errors?.length ? (
                  <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                ) : null}
              </div>
            )}
          </form.Field>

          {loginError && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
              {loginError}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoggingIn || !form.state.canSubmit}
          >
            {isLoggingIn ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}