'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authStorage, apiClient, type User, type LoginCredentials } from '@/lib/auth';

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const queryClient = useQueryClient();

  // Initialize auth state on mount
  useEffect(() => {
    const token = authStorage.getToken();
    const user = authStorage.getUser();
    
    setAuthState({
      user,
      isAuthenticated: !!token && !!user,
      isLoading: false,
    });
  }, []);

  // Get current user query (only runs if authenticated)
  const { data: currentUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: apiClient.getCurrentUser,
    enabled: authState.isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => apiClient.login(credentials),
    onSuccess: (data) => {
      authStorage.setToken(data.access_token);
      authStorage.setUser(data.user);
      
      setAuthState({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });

      queryClient.setQueryData(['currentUser'], data.user);
    },
    onError: (error) => {
      console.error('Login failed:', error);
      logout();
    },
  });

  // Logout function
  const logout = () => {
    authStorage.clear();
    setAuthState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
    queryClient.removeQueries({ queryKey: ['currentUser'] });
    queryClient.clear();
  };

  return {
    ...authState,
    user: currentUser || authState.user,
    login: loginMutation.mutate,
    logout,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error?.message,
  };
}