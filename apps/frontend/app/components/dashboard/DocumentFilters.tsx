'use client';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Search, Filter, FileText, Users, CheckCircle, XCircle, Clock } from 'lucide-react';

interface DocumentFiltersProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  showSent: boolean;
  onShowSentChange: (show: boolean) => void;
  showReceived: boolean;
  onShowReceivedChange: (show: boolean) => void;
  documentCount: number;
  totalCount: number;
}

export function DocumentFilters({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  showSent,
  onShowSentChange,
  showReceived,
  onShowReceivedChange,
  documentCount,
  totalCount,
}: DocumentFiltersProps) {
  const statusOptions = [
    { value: 'all', label: 'All Status', icon: FileText },
    { value: 'active', label: 'Active', icon: CheckCircle },
    { value: 'expired', label: 'Expired', icon: Clock },
    { value: 'deleted', label: 'Deleted', icon: XCircle },
  ];

  const activeFilters = [];
  if (!showSent) activeFilters.push('Sent Hidden');
  if (!showReceived) activeFilters.push('Received Hidden');
  if (statusFilter !== 'all') {
    const status = statusOptions.find(s => s.value === statusFilter);
    if (status) activeFilters.push(status.label);
  }

  return (
    <div className="space-y-4 mb-6">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search documents by title, filename, or sender/recipient..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Filter Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Document Type Toggle */}
        <div className="flex items-center gap-2">
          <Button
            variant={showSent ? 'default' : 'outline'}
            size="sm"
            onClick={() => onShowSentChange(!showSent)}
            className="h-8"
          >
            <FileText className="h-3 w-3 mr-1" />
            Sent
          </Button>
          <Button
            variant={showReceived ? 'default' : 'outline'}
            size="sm"
            onClick={() => onShowReceivedChange(!showReceived)}
            className="h-8"
          >
            <Users className="h-3 w-3 mr-1" />
            Received
          </Button>
        </div>

        {/* Status Filter Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-8">
              <Filter className="h-3 w-3 mr-1" />
              Status
              {statusFilter !== 'all' && (
                <Badge variant="secondary" className="ml-2 h-4 px-1">
                  1
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            {statusOptions.map((option) => {
              const Icon = option.icon;
              return (
                <DropdownMenuItem
                  key={option.value}
                  onClick={() => onStatusFilterChange(option.value)}
                  className={statusFilter === option.value ? 'bg-accent' : ''}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {option.label}
                </DropdownMenuItem>
              );
            })}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Clear Filters */}
        {(searchTerm || activeFilters.length > 0) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              onSearchChange('');
              onStatusFilterChange('all');
              onShowSentChange(true);
              onShowReceivedChange(true);
            }}
            className="h-8 text-muted-foreground"
          >
            Clear filters
          </Button>
        )}
      </div>

      {/* Active Filters & Results Count */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
        <div className="flex flex-wrap items-center gap-2">
          {searchTerm && (
            <Badge variant="outline" className="gap-1">
              Search: &ldquo;{searchTerm}&rdquo;
              <button
                onClick={() => onSearchChange('')}
                className="ml-1 hover:text-foreground"
              >
                ×
              </button>
            </Badge>
          )}
          {activeFilters.map((filter) => (
            <Badge key={filter} variant="outline">
              {filter}
            </Badge>
          ))}
        </div>
        
        <div className="text-right">
          <span className="font-medium">{documentCount}</span>
          {documentCount !== totalCount && (
            <span> of {totalCount}</span>
          )}
          <span> documents</span>
        </div>
      </div>
    </div>
  );
}