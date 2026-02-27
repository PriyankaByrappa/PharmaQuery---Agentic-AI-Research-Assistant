import { cn } from '@/lib/utils';
import { Brain, ArrowDown, Loader2 } from 'lucide-react';

interface MasterAgentVisualizationProps {
  status: 'idle' | 'orchestrating' | 'aggregating' | 'complete';
  query?: string;
}

export const MasterAgentVisualization = ({ status, query }: MasterAgentVisualizationProps) => {
  return (
    <div className="bg-card border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Master Agent</h3>
        <span className={cn(
          "text-xs px-2 py-1 font-medium",
          status === 'idle' && "bg-muted text-muted-foreground",
          status === 'orchestrating' && "bg-primary/10 text-primary",
          status === 'aggregating' && "bg-amber-500/10 text-amber-600",
          status === 'complete' && "bg-emerald-500/10 text-emerald-600"
        )}>
          {status === 'idle' && 'Awaiting Query'}
          {status === 'orchestrating' && 'Orchestrating Agents'}
          {status === 'aggregating' && 'Aggregating Results'}
          {status === 'complete' && 'Analysis Complete'}
        </span>
      </div>

      <div className="flex flex-col items-center py-6">
        <div className={cn(
          "w-16 h-16 flex items-center justify-center border-2 transition-all duration-300",
          status === 'idle' && "border-border bg-muted/50",
          status !== 'idle' && "border-primary bg-primary/10"
        )}>
          {status === 'orchestrating' || status === 'aggregating' ? (
            <Loader2 className="h-8 w-8 text-primary animate-spin" />
          ) : (
            <Brain className={cn(
              "h-8 w-8 transition-colors",
              status === 'idle' ? "text-muted-foreground" : "text-primary"
            )} />
          )}
        </div>

        {query && status !== 'idle' && (
          <div className="mt-4 text-center">
            <p className="text-xs text-muted-foreground mb-1">Processing Query</p>
            <p className="text-sm font-medium max-w-xs truncate">{query}</p>
          </div>
        )}

        {status !== 'idle' && (
          <div className="mt-6 flex flex-col items-center">
            <ArrowDown className="h-5 w-5 text-muted-foreground animate-bounce" />
            <p className="text-xs text-muted-foreground mt-2">
              {status === 'orchestrating' && 'Distributing tasks to worker agents...'}
              {status === 'aggregating' && 'Combining and scoring results...'}
              {status === 'complete' && 'Results ready for review'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
