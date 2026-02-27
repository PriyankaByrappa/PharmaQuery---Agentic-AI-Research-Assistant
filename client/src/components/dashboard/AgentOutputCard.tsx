import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  Shield, 
  FlaskConical, 
  BookOpen,
  CheckCircle
} from 'lucide-react';
import type { AgentStatus, PatentEvidence, ClinicalEvidence, LiteratureEvidence } from '@/lib/api';

interface AgentOutputCardProps {
  agentType: 'market' | 'patent' | 'clinical' | 'literature';
  agentStatus: AgentStatus;
  evidence?: PatentEvidence | ClinicalEvidence | LiteratureEvidence | any;
  score?: number;
  analysisId?: string;
}

export const AgentOutputCard = ({ agentType, agentStatus, evidence, score, analysisId }: AgentOutputCardProps) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    if (analysisId) {
      // Save current scroll position to sessionStorage
      const scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
      sessionStorage.setItem('dashboardScrollPosition', scrollPosition.toString());
      navigate(`/agent/${agentType}/${analysisId}`, {
        state: { analysisId, preserveState: true }
      });
    }
  };
  const getAgentConfig = () => {
    switch (agentType) {
      case 'market':
        return {
          name: 'Market Insights Agent',
          icon: TrendingUp,
          iconColor: 'text-emerald-500',
          bgColor: 'bg-emerald-50/50 dark:bg-emerald-950/20',
          borderColor: 'border-emerald-200 dark:border-emerald-800',
          scoreLabel: 'Market Score'
        };
      case 'patent':
        return {
          name: 'Patent Landscape Agent',
          icon: Shield,
          iconColor: 'text-blue-500',
          bgColor: 'bg-blue-50/50 dark:bg-blue-950/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          scoreLabel: 'Patent Score'
        };
      case 'clinical':
        return {
          name: 'Clinical Trials Agent',
          icon: FlaskConical,
          iconColor: 'text-purple-500',
          bgColor: 'bg-purple-50/50 dark:bg-purple-950/20',
          borderColor: 'border-purple-200 dark:border-purple-800',
          scoreLabel: 'Clinical Score'
        };
      case 'literature':
        return {
          name: 'Regulatory & Literature Agent',
          icon: BookOpen,
          iconColor: 'text-amber-500',
          bgColor: 'bg-amber-50/50 dark:bg-amber-950/20',
          borderColor: 'border-amber-200 dark:border-amber-800',
          scoreLabel: 'Literature Score'
        };
    }
  };

  const config = getAgentConfig();
  const Icon = config.icon;

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-muted-foreground';
    if (score >= 0.8) return 'text-emerald-500';
    if (score >= 0.6) return 'text-amber-500';
    return 'text-muted-foreground';
  };

  const renderMarketOutput = () => {
    if (!evidence) return null;
    return (
      <div className="grid grid-cols-2 gap-3">
        {evidence.cagr && (
          <div className="text-center p-2 bg-muted/30">
            <TrendingUp className="h-4 w-4 mx-auto mb-1 text-emerald-500" />
            <div className="text-sm font-semibold">{evidence.cagr}%</div>
            <div className="text-xs text-muted-foreground">CAGR</div>
          </div>
        )}
        {evidence.market_size && (
          <div className="text-center p-2 bg-muted/30">
            <TrendingUp className="h-4 w-4 mx-auto mb-1 text-emerald-500" />
            <div className="text-sm font-semibold">${(evidence.market_size / 1000000000).toFixed(1)}B</div>
            <div className="text-xs text-muted-foreground">Market Size</div>
          </div>
        )}
        {evidence.competitors && evidence.competitors.length > 0 && (
          <div className="col-span-2 mt-2">
            <p className="text-xs text-muted-foreground mb-2">Competitors</p>
            <div className="flex flex-wrap gap-2">
              {evidence.competitors.slice(0, 5).map((comp: string, index: number) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {comp}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPatentOutput = () => {
    if (!evidence) return null;
    const patentEvidence = evidence as PatentEvidence;
    return (
      <div className="grid grid-cols-4 gap-3">
        <div className="text-center p-2 bg-muted/30">
          <Shield className="h-4 w-4 mx-auto mb-1 text-blue-500" />
          <div className="text-sm font-semibold">{patentEvidence.active_patents ?? 0}</div>
          <div className="text-xs text-muted-foreground">Active</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <Shield className="h-4 w-4 mx-auto mb-1 text-blue-500" />
          <div className="text-sm font-semibold">{patentEvidence.expiring_patents ?? 0}</div>
          <div className="text-xs text-muted-foreground">Expiring</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <Shield className="h-4 w-4 mx-auto mb-1 text-blue-500" />
          <div className="text-sm font-semibold">{patentEvidence.total_patents_found ?? 0}</div>
          <div className="text-xs text-muted-foreground">Total</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <Shield className="h-4 w-4 mx-auto mb-1 text-blue-500" />
          <div className="text-sm font-semibold">{patentEvidence.freedom_to_operate ? 'Yes' : 'No'}</div>
          <div className="text-xs text-muted-foreground">FTO</div>
        </div>
        {patentEvidence.white_space && patentEvidence.white_space.length > 0 && (
          <div className="col-span-4 mt-2">
            <p className="text-xs text-muted-foreground mb-2">White Space</p>
            <div className="flex flex-wrap gap-2">
              {patentEvidence.white_space.slice(0, 3).map((space, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {space}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderClinicalOutput = () => {
    if (!evidence) return null;
    const clinicalEvidence = evidence as ClinicalEvidence;
    const phases = clinicalEvidence.trial_phases || {};
    const phaseEntries = Object.entries(phases).slice(0, 4);
    
    return (
      <div>
        <div className="grid grid-cols-4 gap-3 mb-3">
          <div className="text-center p-2 bg-muted/30">
            <FlaskConical className="h-4 w-4 mx-auto mb-1 text-purple-500" />
            <div className="text-sm font-semibold">{clinicalEvidence.ongoing_trials ?? 0}</div>
            <div className="text-xs text-muted-foreground">Ongoing</div>
          </div>
          <div className="text-center p-2 bg-muted/30">
            <FlaskConical className="h-4 w-4 mx-auto mb-1 text-purple-500" />
            <div className="text-sm font-semibold">{clinicalEvidence.total_trials_found ?? 0}</div>
            <div className="text-xs text-muted-foreground">Total</div>
          </div>
          {phaseEntries.slice(0, 2).map(([phase, count]) => (
            <div key={phase} className="text-center p-2 bg-muted/30">
              <FlaskConical className="h-4 w-4 mx-auto mb-1 text-purple-500" />
              <div className="text-sm font-semibold">{count}</div>
              <div className="text-xs text-muted-foreground">{phase}</div>
            </div>
          ))}
        </div>
        {clinicalEvidence.gaps && clinicalEvidence.gaps.length > 0 && (
          <div className="mt-2">
            <p className="text-xs text-muted-foreground mb-2">Clinical Gaps</p>
            <div className="flex flex-wrap gap-2">
              {clinicalEvidence.gaps.slice(0, 3).map((gap, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {gap}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderLiteratureOutput = () => {
    if (!evidence) return null;
    const literatureEvidence = evidence as LiteratureEvidence;
    return (
      <div className="grid grid-cols-4 gap-3">
        <div className="text-center p-2 bg-muted/30">
          <BookOpen className="h-4 w-4 mx-auto mb-1 text-amber-500" />
          <div className="text-sm font-semibold">{literatureEvidence.article_count ?? 0}</div>
          <div className="text-xs text-muted-foreground">Articles</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <BookOpen className="h-4 w-4 mx-auto mb-1 text-amber-500" />
          <div className="text-sm font-semibold">{literatureEvidence.drug_labels?.length ?? 0}</div>
          <div className="text-xs text-muted-foreground">FDA Labels</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <BookOpen className="h-4 w-4 mx-auto mb-1 text-amber-500" />
          <div className="text-sm font-semibold">{literatureEvidence.black_box_warnings ?? 0}</div>
          <div className="text-xs text-muted-foreground">Warnings</div>
        </div>
        <div className="text-center p-2 bg-muted/30">
          <BookOpen className="h-4 w-4 mx-auto mb-1 text-amber-500" />
          <div className="text-sm font-semibold capitalize">{literatureEvidence.scientific_rationale?.substring(0, 4) ?? 'N/A'}</div>
          <div className="text-xs text-muted-foreground">Rationale</div>
        </div>
      </div>
    );
  };

  const renderEvidence = () => {
    switch (agentType) {
      case 'market':
        return renderMarketOutput();
      case 'patent':
        return renderPatentOutput();
      case 'clinical':
        return renderClinicalOutput();
      case 'literature':
        return renderLiteratureOutput();
    }
  };

  return (
    <div 
      className="bg-card border border-border overflow-hidden cursor-pointer hover:border-primary/50 transition-colors"
      onClick={handleClick}
    >
      {/* Header */}
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded", config.bgColor, config.borderColor, "border")}>
              <Icon className={cn("h-4 w-4", config.iconColor)} />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{config.name}</h3>
              {agentStatus.insights && agentStatus.insights.length > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  {agentStatus.insights[0]}
                </p>
              )}
            </div>
          </div>
          {score !== undefined && (
            <div className="text-right">
              <div className={cn("text-2xl font-bold", getScoreColor(score))}>
                {(score * 100).toFixed(0)}
              </div>
              <p className="text-xs text-muted-foreground">{config.scoreLabel}</p>
            </div>
          )}
        </div>

        {/* Evidence Data - Similar to metric cards */}
        {evidence && (
          <div className="mb-4">
            {renderEvidence()}
          </div>
        )}

        {/* Additional Insights */}
        {agentStatus.insights && agentStatus.insights.length > 1 && (
          <div>
            <p className="text-sm text-muted-foreground">
              {agentStatus.insights.slice(1).join(' • ')}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

