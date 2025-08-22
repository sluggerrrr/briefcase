'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar as CalendarIcon, Clock, Eye, Shield, Info } from 'lucide-react';
import { format } from 'date-fns';

interface SecuritySettingsProps {
  expiresAt: Date | null;
  onExpiresAtChange: (date: Date | null) => void;
  viewLimit: number | null;
  onViewLimitChange: (limit: number | null) => void;
  disabled?: boolean;
}

export function SecuritySettings({
  expiresAt,
  onExpiresAtChange,
  viewLimit,
  onViewLimitChange,
  disabled
}: SecuritySettingsProps) {
  const [calendarOpen, setCalendarOpen] = useState(false);

  // Calculate minimum date (tomorrow)
  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1);
  
  // Calculate maximum date (1 year from now)
  const maxDate = new Date();
  maxDate.setFullYear(maxDate.getFullYear() + 1);

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      // Set time to end of day
      const endOfDay = new Date(date);
      endOfDay.setHours(23, 59, 59, 999);
      onExpiresAtChange(endOfDay);
    } else {
      onExpiresAtChange(null);
    }
    setCalendarOpen(false);
  };

  const handleViewLimitChange = (value: string) => {
    const limit = parseInt(value);
    if (isNaN(limit) || limit < 1) {
      onViewLimitChange(null);
    } else {
      onViewLimitChange(Math.min(limit, 10)); // Max 10 views
    }
  };

  const clearExpiration = () => {
    onExpiresAtChange(null);
  };

  const clearViewLimit = () => {
    onViewLimitChange(null);
  };

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg">Security Settings</CardTitle>
        </div>
        <CardDescription>
          Configure access controls and document lifecycle settings
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Expiration Date */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Expiration Date
            </Label>
            {expiresAt && !disabled && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearExpiration}
                className="h-auto p-1 text-xs text-muted-foreground hover:text-destructive"
              >
                Clear
              </Button>
            )}
          </div>
          
          <div className="space-y-2">
            <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                  disabled={disabled}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {expiresAt ? (
                    <span>{format(expiresAt, 'PPP')}</span>
                  ) : (
                    <span className="text-muted-foreground">Select expiration date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={expiresAt || undefined}
                  onSelect={handleDateSelect}
                  disabled={(date) => date < minDate || date > maxDate}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
            
            {expiresAt && (
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  Expires: {format(expiresAt, 'PPP')}
                </Badge>
              </div>
            )}
            
            <div className="flex items-start gap-2 text-xs text-muted-foreground">
              <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
              <p>
                Document will be automatically deleted after this date. 
                Leave empty for no expiration (maximum 1 year).
              </p>
            </div>
          </div>
        </div>

        {/* View Limit */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="view-limit" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              View Limit
            </Label>
            {viewLimit && !disabled && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearViewLimit}
                className="h-auto p-1 text-xs text-muted-foreground hover:text-destructive"
              >
                Clear
              </Button>
            )}
          </div>
          
          <div className="space-y-2">
            <Input
              id="view-limit"
              type="number"
              min="1"
              max="10"
              placeholder="No limit"
              value={viewLimit || ''}
              onChange={(e) => handleViewLimitChange(e.target.value)}
              disabled={disabled}
              className="w-full"
            />
            
            {viewLimit && (
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  Max {viewLimit} view{viewLimit > 1 ? 's' : ''}
                </Badge>
              </div>
            )}
            
            <div className="flex items-start gap-2 text-xs text-muted-foreground">
              <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
              <p>
                Document access will be blocked after this many views. 
                Leave empty for unlimited views (maximum 10).
              </p>
            </div>
          </div>
        </div>

        {/* Security Summary */}
        {(expiresAt || viewLimit) && (
          <div className="pt-4 border-t">
            <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              Security Summary
            </h4>
            <div className="space-y-1 text-xs text-muted-foreground">
              {expiresAt && (
                <p>• Document expires on {format(expiresAt, 'PPP')}</p>
              )}
              {viewLimit && (
                <p>• Access limited to {viewLimit} view{viewLimit > 1 ? 's' : ''}</p>
              )}
              <p>• Document is encrypted at rest</p>
              <p>• Access is logged and audited</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}