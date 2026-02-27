import { Navbar } from '@/components/landing/Navbar';
import { HeroSection } from '@/components/landing/HeroSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { HowItWorksSection } from '@/components/landing/HowItWorksSection';
import { CTASection } from '@/components/landing/CTASection';
import { Footer } from '@/components/landing/Footer';
import { Helmet } from 'react-helmet-async';

const Index = () => {
  return (
    <>
      <Helmet>
        <title>PharmaQuery - Drug Repurposing Intelligence Platform</title>
        <meta name="description" content="Discover new therapeutic opportunities with AI-powered drug repurposing analysis. Analyze market dynamics, patent landscapes, clinical trials, and scientific literature." />
      </Helmet>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="pt-16">
          <HeroSection />
          <FeaturesSection />
          <HowItWorksSection />
          <CTASection />
        </main>
        <Footer />
      </div>
    </>
  );
};

export default Index;
