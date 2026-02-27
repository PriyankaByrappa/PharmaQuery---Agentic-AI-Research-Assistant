import { Button } from '@/components/ui/button';
import { ArrowRight, Sparkles, FileUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { ResearchUploadModal } from '@/components/research/ResearchUploadModal';

export const HeroSection = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-card to-background" />

      {/* Animated grid pattern */}
      <div className="absolute inset-0 opacity-[0.03]">
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(hsl(var(--primary)) 1px, transparent 1px),
                           linear-gradient(90deg, hsl(var(--primary)) 1px, transparent 1px)`,
          backgroundSize: '60px 60px'
        }} />
      </div>

      <div className="container relative z-10 px-4 md:px-6">
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-8 border border-border bg-card/50 backdrop-blur-sm">
            <Sparkles className="h-4 w-4 text-secondary" />
            <span className="text-sm font-medium text-muted-foreground">
              AI-Powered Research Paper Evaluation & Intelligence
            </span>
          </div>

          {/* Main headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
            <span className="text-foreground">Accelerate Your</span>
            <br />
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Academic Discovery
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-10 leading-relaxed">
            Upload your research paper for IEEE-level evaluation, inline annotations,
            and intelligent discovery of research opportunities and faculty connections.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button asChild size="lg" className="group px-8">
              <Link to="/dashboard">
                Start Analysis
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button
              size="lg"
              variant="secondary"
              className="group px-8"
              onClick={() => setIsUploadModalOpen(true)}
            >
              <FileUp className="mr-2 h-4 w-4" />
              Upload Research Paper
            </Button>
            <Button asChild variant="outline" size="lg" className="px-8">
              <a href="#how-it-works">See How It Works</a>
            </Button>
          </div>

          <ResearchUploadModal
            isOpen={isUploadModalOpen}
            onClose={() => setIsUploadModalOpen(false)}
          />

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 md:gap-16 mt-20 pt-10 border-t border-border">
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-foreground">4</div>
              <div className="text-sm text-muted-foreground mt-1">AI Agents</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-foreground">15+</div>
              <div className="text-sm text-muted-foreground mt-1">Data Sources</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-foreground">Real-time</div>
              <div className="text-sm text-muted-foreground mt-1">Analysis</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
