'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/auth';
import { useErrorHandler } from './useErrorHandler';

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export function useUserSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const { handleError } = useErrorHandler({ 
    showToast: true, 
    redirectOnAuth: true 
  });

  // Fetch all users
  const { data: users = [], isLoading, error } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      return apiClient.request<User[]>('/api/v1/users/');
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false, // Don't retry auth errors
  });

  // Handle errors manually since onError is deprecated in newer React Query versions
  if (error) {
    handleError(error);
  }

  // Filter users based on search term
  const filteredUsers = useMemo(() => {
    if (!searchTerm.trim()) {
      return users;
    }

    const search = searchTerm.toLowerCase();
    return users.filter(user => 
      user.email.toLowerCase().includes(search) ||
      user.name.toLowerCase().includes(search)
    );
  }, [users, searchTerm]);

  return {
    users: filteredUsers,
    searchTerm,
    setSearchTerm,
    isLoading,
    error,
  };
}