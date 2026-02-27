import { 
  Search, 
  Cpu, 
  Layers, 
  BarChart3, 
  FileOutput,
  ArrowRight
} from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Search,
    title: 'Input Query',
    description: 'Enter your drug and target indication to begin the analysis workflow.'
  },
  {
    number: '02',
    icon: Cpu,
    title: 'Master Agent Orchestration',
    description: 'The Master Agent interprets your query and assigns tasks to specialized worker agents.'
  },
  {
    number: '03',
    icon: Layers,
    title: 'Parallel Agent Execution',
    description: 'Market, Patent, Clinical, and Literature agents simultaneously gather and analyze data.'
  },
  {
    number: '04',
    icon: BarChart3,
    title: 'Scoring & Ranking',
    description: 'A transparent scoring engine evaluates and ranks opportunities based on multiple factors.'
  },
  {
    number: '05',
    icon: FileOutput,
    title: 'Report Generation',
    description: 'Receive a comprehensive PDF report with evidence-backed recommendations.'
  }
];

export const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="py-24 bg-background">
      <div className="container px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            From query to actionable insights in minutes—our multi-agent system 
            handles the complexity so you can focus on decision-making.
          </p>
        </div>

        <div className="relative">
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <div className="flex flex-col items-center text-center">
                  {/* Step number with icon */}
                  <div className="relative z-10 w-16 h-16 flex items-center justify-center bg-card border-2 border-primary mb-4">
                    <step.icon className="h-7 w-7 text-primary" />
                  </div>
                  
                  {/* Step number badge */}
                  <span className="absolute -top-2 -right-2 w-8 h-8 flex items-center justify-center bg-primary text-primary-foreground text-xs font-bold z-20">
                    {step.number}
                  </span>

                  <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Arrow for mobile/tablet */}
                {index < steps.length - 1 && (
                  <div className="hidden md:flex lg:hidden absolute -bottom-4 left-1/2 -translate-x-1/2">
                    <ArrowRight className="h-6 w-6 text-muted rotate-90 md:rotate-0" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
