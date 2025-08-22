'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/auth';

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export function useUserSearch() {
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch all users
  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      return apiClient.request<User[]>('/api/v1/users');
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Filter users based on search term
  const filteredUsers = useMemo(() => {
    if (!searchTerm.trim()) {
      return users;
    }

    const search = searchTerm.toLowerCase();
    return users.filter(user => 
      user.email.toLowerCase().includes(search) ||
      (user.name && user.name.toLowerCase().includes(search))
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