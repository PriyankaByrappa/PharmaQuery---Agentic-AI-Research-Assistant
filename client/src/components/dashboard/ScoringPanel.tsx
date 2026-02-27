import { Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const scoringWeights = [
  { name: 'Market Score', weight: 0.30, description: 'Demand, competition, CAGR analysis' },
  { name: 'Patent Score', weight: 0.25, description: 'FTO, expiry clusters, density' },
  { name: 'Clinical Score', weight: 0.25, description: 'Trial count, gaps, unmet needs' },
  { name: 'Literature Score', weight: 0.20, description: 'Scientific rationale, regulatory status' }
];

export const ScoringPanel = () => {
  return (
    <div className="bg-card border border-border p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Scoring Methodology</h3>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <Info className="h-4 w-4 text-muted-foreground" />
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              <p className="text-sm">
                Final Score = Σ(Weight × Component Score). 
                Weights are configurable based on strategic priorities.
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <div className="space-y-3">
        {scoringWeights.map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{item.name}</span>
                <span className="text-sm text-muted-foreground">{(item.weight * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 bg-muted overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-500"
                  style={{ width: `${item.weight * 100}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs text-muted-foreground">
          <strong>Formula:</strong> 0.30×(Market) + 0.25×(Patent) + 0.25×(Clinical) + 0.20×(Literature)
        </p>
      </div>
    </div>
  );
};
