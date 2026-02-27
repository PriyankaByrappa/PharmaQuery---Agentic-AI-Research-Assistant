import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const CTASection = () => {
  return (
    <section className="py-24 bg-primary">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-primary-foreground">
            Ready to Discover New Opportunities?
          </h2>
          <p className="text-primary-foreground/80 text-lg mb-8 leading-relaxed">
            Start your drug repurposing analysis today and unlock evidence-backed 
            therapeutic opportunities powered by multi-agent AI intelligence.
          </p>
          <Button 
            asChild 
            size="lg" 
            variant="secondary"
            className="group px-8"
          >
            <Link to="/dashboard">
              Launch Dashboard
              <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
};
