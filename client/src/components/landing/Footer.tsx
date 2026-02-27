import { Dna } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="py-12 bg-card border-t border-border">
      <div className="container px-4 md:px-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <Dna className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">PharmaQuery</span>
          </div>

          <nav className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
            <Link to="/" className="hover:text-foreground transition-colors">Home</Link>
            <Link to="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link>
            <a href="#how-it-works" className="hover:text-foreground transition-colors">How It Works</a>
            <a href="#" className="hover:text-foreground transition-colors">Documentation</a>
          </nav>

          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} PharmaQuery. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};
