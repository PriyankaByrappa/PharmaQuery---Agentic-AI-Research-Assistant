import { cn } from '@/lib/utils';
import { 
  TrendingUp, 
  Shield, 
  FlaskConical, 
  BookOpen,
  CheckCircle2,
  Loader2,
  Circle
} from 'lucide-react';
import type { AgentResult } from '@/lib/mockData';

interface AgentCardProps {
  type: 'market' | 'patent' | 'clinical' | 'literature';
  result: AgentResult;
}

const agentConfig = {
  market: {
    icon: TrendingUp,
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/30'
  },
  patent: {
    icon: Shield,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30'
  },
  clinical: {
    icon: FlaskConical,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30'
  },
  literature: {
    icon: BookOpen,
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30'
  }
};

export const AgentCard = ({ type, result }: AgentCardProps) => {
  const config = agentConfig[type];
  const Icon = config.icon;

  const StatusIcon = () => {
    switch (result.status) {
      case 'complete':
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-primary animate-spin" />;
      case 'error':
        return <Circle className="h-5 w-5 text-destructive" />;
      default:
        return <Circle className="h-5 w-5 text-muted" />;
    }
  };

  return (
    <div className={cn(
      "bg-card border p-5 transition-all duration-300",
      result.status === 'running' && "border-primary/50 shadow-lg",
      result.status === 'complete' && config.borderColor,
      result.status === 'idle' && "border-border"
    )}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn("w-10 h-10 flex items-center justify-center", config.bgColor)}>
            <Icon className={cn("h-5 w-5", config.color)} />
          </div>
          <div>
            <h3 className="font-semibold text-sm">{result.agentName}</h3>
            <p className="text-xs text-muted-foreground capitalize">{result.status}</p>
          </div>
        </div>
        <StatusIcon />
      </div>

      {result.status === 'complete' && result.insights.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Key Insights</p>
          <ul className="space-y-1.5">
            {result.insights.slice(0, 3).map((insight, index) => (
              <li key={index} className="text-xs text-foreground/80 flex items-start gap-2">
                <span className={cn("mt-1.5 w-1 h-1 rounded-full flex-shrink-0", config.bgColor.replace('/10', ''))} />
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
