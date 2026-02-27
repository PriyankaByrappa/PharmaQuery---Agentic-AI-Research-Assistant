import { 
  TrendingUp, 
  Shield, 
  FlaskConical, 
  BookOpen,
  Brain,
  FileText
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const features = [
  {
    icon: TrendingUp,
    title: 'Market Intelligence',
    description: 'Real-time market sizing, CAGR analysis, competitor mapping, and demand forecasting across therapeutic areas.'
  },
  {
    icon: Shield,
    title: 'Patent Landscape',
    description: 'Comprehensive patent analysis including expiry timelines, freedom-to-operate assessment, and white space identification.'
  },
  {
    icon: FlaskConical,
    title: 'Clinical Trial Analysis',
    description: 'Deep analysis of ongoing trials, phase distributions, evidence gaps, and unmet medical needs.'
  },
  {
    icon: BookOpen,
    title: 'Literature & Regulatory',
    description: 'Scientific rationale extraction, regulatory guidance mapping, and safety signal monitoring.'
  },
  {
    icon: Brain,
    title: 'Multi-Agent AI',
    description: 'Orchestrated AI agents work in parallel to gather, analyze, and synthesize insights from multiple data sources.'
  },
  {
    icon: FileText,
    title: 'Decision-Ready Reports',
    description: 'Auto-generated PDF reports with ranked opportunities, evidence summaries, and strategic recommendations.'
  }
];

export const FeaturesSection = () => {
  return (
    <section className="py-24 bg-card">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Comprehensive Intelligence Platform
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Six integrated capabilities powered by specialized AI agents working together
            to uncover high-value drug repurposing opportunities.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="group border-border bg-background hover:border-primary/50 transition-all duration-300"
            >
              <CardContent className="p-6">
                <div className="w-12 h-12 flex items-center justify-center bg-primary/10 text-primary mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
