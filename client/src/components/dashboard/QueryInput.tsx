import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, Loader2 } from 'lucide-react';
import { useState } from 'react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export const QueryInput = ({ onSubmit, isLoading }: QueryInputProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  const exampleQueries = [
    'Find repurposing opportunities for Metformin in oncology',
    'Analyze Thalidomide for autoimmune diseases',
    'Evaluate Propranolol for anxiety disorders'
  ];

  return (
    <div className="bg-card border border-border p-6 md:p-8">
      <h2 className="text-xl font-semibold mb-2">Drug Repurposing Query</h2>
      <p className="text-muted-foreground text-sm mb-6">
        Enter a drug name and target indication to analyze repurposing opportunities
      </p>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="e.g., Find repurposing opportunities for Drug X in oncology"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-10 h-12"
            disabled={isLoading}
          />
        </div>
        <Button type="submit" disabled={isLoading || !query.trim()} className="h-12 px-6">
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing
            </>
          ) : (
            'Analyze'
          )}
        </Button>
      </form>

      <div className="mt-4">
        <p className="text-xs text-muted-foreground mb-2">Try an example:</p>
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="text-xs px-3 py-1.5 bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors border border-border"
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
