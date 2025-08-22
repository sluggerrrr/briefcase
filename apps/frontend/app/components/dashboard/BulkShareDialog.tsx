'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Share, 
  Users, 
  
  X, 
  CheckCircle, 
  XCircle,
  Calendar,
  Eye
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';
import { useBulkOperations } from '@/hooks/useBulkOperations';
import { useUserSearch } from '@/hooks/useUserSearch';
import { toast } from 'sonner';

interface BulkShareDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentIds: string[];
  documentCount: number;
}

interface ShareResult {
  documentId: string;
  status: 'pending' | 'success' | 'failed' | 'permission_denied';
  error?: string;
}

interface BulkOperationResult {
  document_id: string;
  status: 'success' | 'failed' | 'permission_denied';
  error?: string;
}

interface SelectedUser {
  id: string;
  email: string;
}

export function BulkShareDialog({
  open,
  onOpenChange,
  documentIds,
  documentCount
}: BulkShareDialogProps) {
  const [isSharing, setIsSharing] = useState(false);
  const [shareResults, setShareResults] = useState<ShareResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  
  // Form state
  const [selectedUsers, setSelectedUsers] = useState<SelectedUser[]>([]);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [permissionType, setPermissionType] = useState<string>('read');
  const [expiresAt, setExpiresAt] = useState<Date | undefined>();

  const { bulkShare } = useBulkOperations();
  const { data: searchResults, isLoading: isSearching } = useUserSearch(userSearchQuery);

  const handleAddUser = (user: { id: string; email: string }) => {
    if (!selectedUsers.find(u => u.id === user.id)) {
      setSelectedUsers([...selectedUsers, user]);
    }
    setUserSearchQuery('');
  };

  const handleRemoveUser = (userId: string) => {
    setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
  };

  const handleShare = async () => {
    if (selectedUsers.length === 0) {
      toast.error('Please select at least one user to share with');
      return;
    }

    setIsSharing(true);
    setShowResults(true);

    // Initialize results
    const initialResults: ShareResult[] = documentIds.map(id => ({
      documentId: id,
      status: 'pending'
    }));
    setShareResults(initialResults);

    try {
      const result = await bulkShare({
        document_ids: documentIds,
        recipient_ids: selectedUsers.map(u => u.id),
        permission_type: permissionType,
        expires_at: expiresAt?.toISOString()
      });
      
      // Update results based on API response
      const updatedResults = result.results.map((apiResult: BulkOperationResult) => ({
        documentId: apiResult.document_id,
        status: apiResult.status,
        error: apiResult.error
      }));
      
      setShareResults(updatedResults);

      // Show summary toast
      if (result.successful > 0) {
        toast.success(
          `Successfully shared ${result.successful} document${result.successful > 1 ? 's' : ''} with ${selectedUsers.length} user${selectedUsers.length > 1 ? 's' : ''}`
        );
      }
      
      if (result.failed > 0) {
        toast.error(`Failed to share ${result.failed} document${result.failed > 1 ? 's' : ''}`);
      }

    } catch (error) {
      console.error('Bulk share error:', error);
      toast.error('Failed to share documents');
      
      // Mark all as failed
      setShareResults(prev =>
        prev.map(result => ({
          ...result,
          status: 'failed',
          error: 'Network error'
        }))
      );
    } finally {
      setIsSharing(false);
    }
  };

  const handleClose = () => {
    if (isSharing) return; // Prevent closing during operation
    
    setSelectedUsers([]);
    setUserSearchQuery('');
    setPermissionType('read');
    setExpiresAt(undefined);
    setShowResults(false);
    setShareResults([]);
    onOpenChange(false);
  };

  const getResultIcon = (status: ShareResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
      case 'permission_denied':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-muted animate-spin" />;
    }
  };

  const getResultText = (result: ShareResult) => {
    switch (result.status) {
      case 'success':
        return 'Shared successfully';
      case 'permission_denied':
        return 'Permission denied';
      case 'failed':
        return result.error || 'Share failed';
      default:
        return 'Sharing...';
    }
  };

  const completedCount = shareResults.filter(r => r.status !== 'pending').length;
  const progressPercentage = documentCount > 0 ? (completedCount / documentCount) * 100 : 0;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share className="h-5 w-5 text-primary" />
            Share Documents
          </DialogTitle>
          <DialogDescription>
            {showResults ? (
              `Sharing ${documentCount} document${documentCount > 1 ? 's' : ''} with ${selectedUsers.length} user${selectedUsers.length > 1 ? 's' : ''}...`
            ) : (
              `Share ${documentCount} document${documentCount > 1 ? 's' : ''} with selected users and configure permissions.`
            )}
          </DialogDescription>
        </DialogHeader>

        {showResults ? (
          <div className="space-y-4">
            {/* Progress */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{completedCount} of {documentCount}</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>

            {/* Results List */}
            <ScrollArea className="max-h-48">
              <div className="space-y-2">
                {shareResults.map((result) => (
                  <div
                    key={result.documentId}
                    className="flex items-center justify-between p-2 rounded-md bg-muted/50"
                  >
                    <div className="flex items-center gap-2">
                      {getResultIcon(result.status)}
                      <span className="text-sm font-mono text-muted-foreground">
                        {result.documentId.slice(0, 8)}...
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {getResultText(result)}
                    </span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        ) : (
          <div className="space-y-6">
            {/* User Selection */}
            <div className="space-y-3">
              <Label htmlFor="user-search">Select Users</Label>
              
              {/* Selected Users */}
              {selectedUsers.length > 0 && (
                <div className="flex flex-wrap gap-2 p-2 bg-muted/50 rounded-md">
                  {selectedUsers.map((user) => (
                    <Badge key={user.id} variant="secondary" className="gap-1">
                      {user.email}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-3 w-3 hover:bg-destructive/20"
                        onClick={() => handleRemoveUser(user.id)}
                      >
                        <X className="h-2 w-2" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              )}

              {/* User Search */}
              <div className="relative">
                <Input
                  id="user-search"
                  placeholder="Search for users by email..."
                  value={userSearchQuery}
                  onChange={(e) => setUserSearchQuery(e.target.value)}
                />
                
                {/* Search Results */}
                {userSearchQuery && (
                  <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-background border rounded-md shadow-lg max-h-32 overflow-y-auto">
                    {isSearching ? (
                      <div className="p-2 text-sm text-muted-foreground">Searching...</div>
                    ) : searchResults?.length ? (
                      searchResults.map((user) => (
                        <button
                          key={user.id}
                          className="w-full text-left p-2 hover:bg-muted text-sm"
                          onClick={() => handleAddUser(user)}
                        >
                          <div className="flex items-center gap-2">
                            <Users className="h-3 w-3" />
                            {user.email}
                          </div>
                        </button>
                      ))
                    ) : (
                      <div className="p-2 text-sm text-muted-foreground">No users found</div>
                    )}
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Permission Settings */}
            <div className="space-y-4">
              <Label>Permission Settings</Label>
              
              <div className="grid grid-cols-2 gap-4">
                {/* Permission Type */}
                <div className="space-y-2">
                  <Label htmlFor="permission-type" className="text-sm">Permission Level</Label>
                  <Select value={permissionType} onValueChange={setPermissionType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="read">
                        <div className="flex items-center gap-2">
                          <Eye className="h-3 w-3" />
                          Read Only
                        </div>
                      </SelectItem>
                      <SelectItem value="write">
                        <div className="flex items-center gap-2">
                          <Share className="h-3 w-3" />
                          Read & Write
                        </div>
                      </SelectItem>
                      <SelectItem value="share">
                        <div className="flex items-center gap-2">
                          <Users className="h-3 w-3" />
                          Can Share
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Expiration Date */}
                <div className="space-y-2">
                  <Label className="text-sm">Expires (Optional)</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
                      >
                        <Calendar className="h-3 w-3 mr-2" />
                        {expiresAt ? format(expiresAt, 'PPP') : 'No expiration'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <CalendarComponent
                        mode="single"
                        selected={expiresAt}
                        onSelect={setExpiresAt}
                        disabled={(date) => date < new Date()}
                        initialFocus
                      />
                      {expiresAt && (
                        <div className="p-2 border-t">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="w-full"
                            onClick={() => setExpiresAt(undefined)}
                          >
                            Clear expiration
                          </Button>
                        </div>
                      )}
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
            </div>
          </div>
        )}

        <DialogFooter>
          {showResults ? (
            <Button
              onClick={handleClose}
              disabled={isSharing}
              className="w-full"
            >
              {isSharing ? 'Sharing...' : 'Close'}
            </Button>
          ) : (
            <div className="flex gap-2 w-full">
              <Button
                variant="outline"
                onClick={handleClose}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleShare}
                disabled={selectedUsers.length === 0}
                className="flex-1"
              >
                <Share className="h-4 w-4 mr-2" />
                Share with {selectedUsers.length}
              </Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}