'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useUserSearch, type User } from '@/hooks/useUserSearch';
import { useAuth } from '@/hooks/useAuth';
import { Check, ChevronDown, Search, Users, X } from 'lucide-react';

interface RecipientSelectorProps {
  selectedRecipient: User | null;
  onRecipientChange: (recipient: User | null) => void;
  error?: string;
  disabled?: boolean;
}

export function RecipientSelector({ 
  selectedRecipient, 
  onRecipientChange, 
  error,
  disabled 
}: RecipientSelectorProps) {
  // Explicitly type selectedRecipient to help TypeScript
  const currentSelection: User | null = selectedRecipient;
  const [open, setOpen] = useState(false);
  const { users, searchTerm, setSearchTerm, isLoading } = useUserSearch();
  const { user: currentUser } = useAuth();

  // Filter out current user from recipients  
  const availableUsers = (users as User[]).filter(user => user.id !== currentUser?.id);

  const handleSelect = (user: User) => {
    onRecipientChange(user);
    setOpen(false);
    setSearchTerm('');
  };

  const handleClear = () => {
    onRecipientChange(null);
    setSearchTerm('');
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="recipient">
        Recipient <span className="text-destructive">*</span>
      </Label>
      
      <div className="space-y-2">
        {selectedRecipient ? (
          <div className="flex items-center gap-2 p-2 border rounded-md bg-muted/50">
            <Users className="h-4 w-4 text-muted-foreground" />
            <div className="flex-1">
              <p className="font-medium text-sm">{selectedRecipient.name}</p>
              <p className="text-xs text-muted-foreground">{selectedRecipient.email}</p>
            </div>
            {!disabled && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 hover:bg-destructive/10 hover:text-destructive"
                onClick={handleClear}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
        ) : (
          <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={open}
                className="w-full justify-between"
                disabled={disabled}
              >
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    Select recipient...
                  </span>
                </div>
                <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-full p-0" align="start">
              <Command>
                <CommandInput 
                  placeholder="Search users by email or name..."
                  value={searchTerm}
                  onValueChange={setSearchTerm}
                />
                <CommandList>
                  {isLoading ? (
                    <CommandEmpty>Loading users...</CommandEmpty>
                  ) : availableUsers.length === 0 ? (
                    <CommandEmpty>
                      {searchTerm ? 'No users found.' : 'No other users available.'}
                    </CommandEmpty>
                  ) : (
                                         <CommandGroup>
                       {availableUsers.map((user) => {
                        const isSelected = currentSelection && currentSelection.id === user.id;
                        
                        return (
                          <CommandItem
                            key={user.id}
                            value={user.email}
                            onSelect={() => handleSelect(user)}
                            className="flex items-center gap-2"
                          >
                            <div className="flex items-center gap-2 flex-1">
                              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                <Users className="h-4 w-4 text-primary" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-sm truncate">{user.name}</p>
                                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                              </div>
                            </div>
                            {isSelected && (
                              <Check className="h-4 w-4" />
                            )}
                          </CommandItem>
                        );
                      })}
                    </CommandGroup>
                  )}
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        )}
      </div>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      <div className="text-xs text-muted-foreground">
        <p>Select a user to share this document with. Only the selected recipient will be able to access the document.</p>
      </div>
    </div>
  );
}