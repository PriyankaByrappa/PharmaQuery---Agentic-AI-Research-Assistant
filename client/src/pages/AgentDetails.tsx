import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Navbar } from '@/components/landing/Navbar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  Shield, 
  FlaskConical, 
  BookOpen,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  ExternalLink
} from 'lucide-react';
import { apiClient, type AgentStatus, type AgentOutput } from '@/lib/api';
import { toast } from 'sonner';

type AgentType = 'market' | 'patent' | 'clinical' | 'literature';

const AgentDetails = () => {
  const { agentType, analysisId } = useParams<{ agentType: AgentType; analysisId: string }>();
  const navigate = useNavigate();
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [agentOutput, setAgentOutput] = useState<AgentOutput | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!agentType || !analysisId) {
      toast.error('Invalid agent or analysis ID');
      navigate('/dashboard');
      return;
    }

    const loadAgentData = async () => {
      try {
        const status = await apiClient.getAnalysisStatus(analysisId);
        const agent = status.agents[agentType];
        const output = status.agent_outputs?.[agentType];

        if (agent) {
          setAgentStatus(agent);
        }
        if (output) {
          setAgentOutput(output);
        }
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading agent data:', error);
        toast.error('Failed to load agent details');
        setIsLoading(false);
      }
    };

    loadAgentData();
  }, [agentType, analysisId, navigate]);

  const getAgentConfig = () => {
    switch (agentType) {
      case 'market':
        return {
          name: 'Market Insights Agent',
          icon: TrendingUp,
          iconColor: 'text-emerald-500',
          bgColor: 'bg-emerald-50/50 dark:bg-emerald-950/20',
          borderColor: 'border-emerald-200 dark:border-emerald-800',
          scoreLabel: 'Market Score',
          description: 'Market size, growth, competition, and commercial viability analysis'
        };
      case 'patent':
        return {
          name: 'Patent Landscape Agent',
          icon: Shield,
          iconColor: 'text-blue-500',
          bgColor: 'bg-blue-50/50 dark:bg-blue-950/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          scoreLabel: 'Patent Score',
          description: 'Patent analysis, freedom to operate, and IP landscape assessment'
        };
      case 'clinical':
        return {
          name: 'Clinical Trials Agent',
          icon: FlaskConical,
          iconColor: 'text-purple-500',
          bgColor: 'bg-purple-50/50 dark:bg-purple-950/20',
          borderColor: 'border-purple-200 dark:border-purple-800',
          scoreLabel: 'Clinical Score',
          description: 'Clinical trial analysis, gaps, and unmet medical needs'
        };
      case 'literature':
        return {
          name: 'Regulatory & Literature Agent',
          icon: BookOpen,
          iconColor: 'text-amber-500',
          bgColor: 'bg-amber-50/50 dark:bg-amber-950/20',
          borderColor: 'border-amber-200 dark:border-amber-800',
          scoreLabel: 'Literature Score',
          description: 'Scientific literature, regulatory status, and safety analysis'
        };
    }
  };

  const config = getAgentConfig();
  const Icon = config.icon;
  const score = agentOutput?.scores?.[agentType === 'market' ? 'market_potential' : 
                                      agentType === 'patent' ? 'patent_score' :
                                      agentType === 'clinical' ? 'clinical_score' : 'literature_score'];

  const getScoreColor = (score?: number) => {
    if (!score) return 'text-muted-foreground';
    if (score >= 0.8) return 'text-emerald-500';
    if (score >= 0.6) return 'text-amber-500';
    return 'text-muted-foreground';
  };

  if (isLoading) {
    return (
      <>
        <Helmet>
          <title>Loading Agent Details - PharmaQuery</title>
        </Helmet>
        <div className="min-h-screen bg-background">
          <Navbar />
          <main className="pt-20 pb-12">
            <div className="container px-4 md:px-6">
              <div className="text-center py-12">
                <p className="text-muted-foreground">Loading agent details...</p>
              </div>
            </div>
          </main>
        </div>
      </>
    );
  }

  if (!agentStatus || !agentOutput) {
    return (
      <>
        <Helmet>
          <title>Agent Not Found - PharmaQuery</title>
        </Helmet>
        <div className="min-h-screen bg-background">
          <Navbar />
          <main className="pt-20 pb-12">
            <div className="container px-4 md:px-6">
              <div className="text-center py-12">
                <p className="text-muted-foreground">Agent data not found</p>
                <Button onClick={() => navigate('/dashboard')} className="mt-4">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Dashboard
                </Button>
              </div>
            </div>
          </main>
        </div>
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>{config.name} - PharmaQuery</title>
      </Helmet>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="pt-20 pb-12">
          <div className="container px-4 md:px-6 max-w-6xl">
            {/* Header */}
            <div className="mb-8">
              <Button
                variant="ghost"
                onClick={() => navigate('/dashboard', { state: { analysisId, preserveState: true } })}
                className="mb-4"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Button>
              
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg ${config.bgColor} ${config.borderColor} border`}>
                    <Icon className={`h-8 w-8 ${config.iconColor}`} />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold">{config.name}</h1>
                    <p className="text-muted-foreground mt-1">{config.description}</p>
                  </div>
                </div>
                {score !== undefined && (
                  <div className="text-right">
                    <div className={`text-4xl font-bold ${getScoreColor(score)}`}>
                      {(score * 100).toFixed(0)}
                    </div>
                    <p className="text-sm text-muted-foreground">{config.scoreLabel}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Status Card */}
            <div className="bg-card border border-border rounded-lg p-6 mb-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Agent Status</h2>
                <Badge variant={agentStatus.status === 'complete' ? 'default' : 'secondary'}>
                  {agentStatus.status.toUpperCase()}
                </Badge>
              </div>
            </div>

            {/* Insights */}
            {agentStatus.insights && agentStatus.insights.length > 0 && (
              <div className="bg-card border border-border rounded-lg p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-500" />
                  Key Insights
                </h2>
                <ul className="space-y-3">
                  {agentStatus.insights.map((insight, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0" />
                      <p className="text-sm text-foreground">{insight}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Detailed Evidence */}
            {agentOutput.evidence && (
              <div className="bg-card border border-border rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-6">Detailed Evidence</h2>
                {renderDetailedEvidence(agentType, agentOutput.evidence)}
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
};

const renderDetailedEvidence = (agentType: AgentType, evidence: any) => {
  switch (agentType) {
    case 'market':
      return renderMarketDetails(evidence);
    case 'patent':
      return renderPatentDetails(evidence);
    case 'clinical':
      return renderClinicalDetails(evidence);
    case 'literature':
      return renderLiteratureDetails(evidence);
  }
};

const renderMarketDetails = (evidence: any) => {
  return (
    <div className="space-y-6">
      {/* Market Metrics */}
      <div className="grid md:grid-cols-3 gap-4">
        {evidence.market_size && (
          <div className="p-4 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Market Size</p>
            <p className="text-2xl font-bold">${(evidence.market_size / 1000000000).toFixed(1)}B</p>
          </div>
        )}
        {evidence.cagr && (
          <div className="p-4 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">CAGR</p>
            <p className="text-2xl font-bold">{evidence.cagr}%</p>
          </div>
        )}
        {evidence.demand_trends && (
          <div className="p-4 bg-muted/30 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Demand Trends</p>
            <p className="text-2xl font-bold capitalize">{evidence.demand_trends.replace('_', ' ')}</p>
          </div>
        )}
      </div>

      {/* Competitors */}
      {evidence.competitors && evidence.competitors.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Competitors</h3>
          <div className="flex flex-wrap gap-2">
            {evidence.competitors.map((comp: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-sm py-2 px-4">
                {comp}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Geographical Hotspots */}
      {evidence.geographical_hotspots && evidence.geographical_hotspots.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Geographical Hotspots</h3>
          <div className="flex flex-wrap gap-2">
            {evidence.geographical_hotspots.map((hotspot: string, index: number) => (
              <Badge key={index} variant="outline" className="text-sm py-2 px-4">
                {hotspot}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Methodology */}
      {evidence.methodology && (
        <div className="p-4 bg-muted/20 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Methodology</p>
          <p className="text-sm font-medium">{evidence.methodology.replace('_', ' ')}</p>
        </div>
      )}
    </div>
  );
};

const renderPatentDetails = (evidence: any) => {
  return (
    <div className="space-y-6">
      {/* Patent Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Active Patents</p>
          <p className="text-2xl font-bold">{evidence.active_patents ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Expiring Patents</p>
          <p className="text-2xl font-bold">{evidence.expiring_patents ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Total Patents</p>
          <p className="text-2xl font-bold">{evidence.total_patents_found ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Freedom to Operate</p>
          <p className="text-2xl font-bold">{evidence.freedom_to_operate ? 'Yes' : 'No'}</p>
        </div>
      </div>

      {/* Patent Density */}
      {evidence.patent_density && (
        <div>
          <h3 className="font-semibold mb-3">Patent Density</h3>
          <Badge variant="secondary" className="text-sm py-2 px-4 capitalize">
            {evidence.patent_density}
          </Badge>
        </div>
      )}

      {/* White Space */}
      {evidence.white_space && evidence.white_space.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">White Space Opportunities</h3>
          <div className="flex flex-wrap gap-2">
            {evidence.white_space.map((space: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-sm py-2 px-4">
                {space}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Patent Details */}
      {evidence.patent_details && evidence.patent_details.length > 0 && (
        <div>
          <h3 className="font-semibold mb-4">Patent Details ({evidence.patent_details.length} patents)</h3>
          <div className="space-y-3">
            {evidence.patent_details.map((patent: any, index: number) => {
              const patentNumber = patent.patent_number?.replace(/[^0-9]/g, '') || '';
              const googlePatentsUrl = patentNumber ? `https://patents.google.com/patent/US${patentNumber}` : null;
              
              return (
              <div 
                key={index} 
                className="p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 cursor-pointer transition-colors"
                onClick={() => {
                  if (googlePatentsUrl) {
                    window.open(googlePatentsUrl, '_blank', 'noopener,noreferrer');
                  }
                }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{patent.patent_number}</p>
                      {googlePatentsUrl && (
                        <ExternalLink className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{patent.title}</p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {patent.source || 'Unknown'}
                  </Badge>
                </div>
                <div className="grid md:grid-cols-3 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Filed</p>
                    <p className="font-medium">{patent.date}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Expires</p>
                    <p className="font-medium">{patent.expiry_date}</p>
                  </div>
                  {patent.assignee && (
                    <div>
                      <p className="text-xs text-muted-foreground">Assignee</p>
                      <p className="font-medium">{patent.assignee}</p>
                    </div>
                  )}
                </div>
                {patent.cpc_class && patent.cpc_class.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-1">CPC Classes</p>
                    <div className="flex flex-wrap gap-1">
                      {patent.cpc_class.map((cpc: string, idx: number) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {cpc}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Expiring Patents */}
      {evidence.expiring_patent_details && evidence.expiring_patent_details.length > 0 && (
        <div>
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Expiring Patents (within 5 years) ({evidence.expiring_patent_details.length} patents)
          </h3>
          <div className="space-y-3">
            {evidence.expiring_patent_details.map((patent: any, index: number) => {
              const patentNumber = patent.patent_number?.replace(/[^0-9]/g, '') || '';
              const googlePatentsUrl = patentNumber ? `https://patents.google.com/patent/US${patentNumber}` : null;
              
              return (
              <div 
                key={index} 
                className="p-4 bg-amber-50/50 dark:bg-amber-950/20 rounded-lg border border-amber-200 dark:border-amber-800 hover:border-amber-400 cursor-pointer transition-colors"
                onClick={() => {
                  if (googlePatentsUrl) {
                    window.open(googlePatentsUrl, '_blank', 'noopener,noreferrer');
                  }
                }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{patent.patent_number}</p>
                      {googlePatentsUrl && (
                        <ExternalLink className="h-4 w-4 text-blue-500" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{patent.title}</p>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Filed</p>
                    <p className="font-medium">{patent.date}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Expires</p>
                    <p className="font-medium text-amber-600 dark:text-amber-400">{patent.expiry_date}</p>
                  </div>
                  {patent.assignee && (
                    <div className="md:col-span-2">
                      <p className="text-xs text-muted-foreground">Assignee</p>
                      <p className="font-medium">{patent.assignee}</p>
                    </div>
                  )}
                </div>
              </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

const renderClinicalDetails = (evidence: any) => {
  return (
    <div className="space-y-6">
      {/* Clinical Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Ongoing Trials</p>
          <p className="text-2xl font-bold">{evidence.ongoing_trials ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Total Trials</p>
          <p className="text-2xl font-bold">{evidence.total_trials_found ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Trial Failures</p>
          <p className="text-2xl font-bold">{evidence.trial_failures ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Clinical Gaps</p>
          <p className="text-2xl font-bold">{evidence.gaps?.length ?? 0}</p>
        </div>
      </div>

      {/* Trial Phases */}
      {evidence.trial_phases && Object.keys(evidence.trial_phases).length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Trial Phases Distribution</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(evidence.trial_phases).map(([phase, count]) => (
              <Badge key={phase} variant="secondary" className="text-sm py-2 px-4">
                {phase}: {count}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Clinical Gaps */}
      {evidence.gaps && evidence.gaps.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Clinical Gaps
          </h3>
          <div className="flex flex-wrap gap-2">
            {evidence.gaps.map((gap: string, index: number) => (
              <Badge key={index} variant="outline" className="text-sm py-2 px-4">
                {gap}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Unmet Needs */}
      {evidence.unmet_needs && evidence.unmet_needs.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Unmet Medical Needs</h3>
          <div className="flex flex-wrap gap-2">
            {evidence.unmet_needs.map((need: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-sm py-2 px-4">
                {need}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Ongoing Trial Details */}
      {evidence.ongoing_trial_details && evidence.ongoing_trial_details.length > 0 && (
        <div>
          <h3 className="font-semibold mb-4">Ongoing Trials ({evidence.ongoing_trial_details.length} trials)</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {evidence.ongoing_trial_details.map((trial: any, index: number) => (
              <div key={index} className="p-4 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold">{trial.nct_id}</p>
                    <p className="text-sm text-muted-foreground mt-1">{trial.title}</p>
                  </div>
                  <a
                    href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
                <div className="grid md:grid-cols-3 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Phase</p>
                    <p className="font-medium">{trial.phase}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Status</p>
                    <p className="font-medium">{trial.status}</p>
                  </div>
                  {trial.start_date && (
                    <div>
                      <p className="text-xs text-muted-foreground">Start Date</p>
                      <p className="font-medium">{trial.start_date}</p>
                    </div>
                  )}
                </div>
                {trial.condition && (
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-1">Condition</p>
                    <p className="text-sm font-medium">{trial.condition}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Trial Details */}
      {evidence.trial_details && evidence.trial_details.length > 0 && 
       (!evidence.ongoing_trial_details || evidence.ongoing_trial_details.length === 0) && (
        <div>
          <h3 className="font-semibold mb-4">Trial Details ({evidence.trial_details.length} trials)</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {evidence.trial_details.map((trial: any, index: number) => (
              <div key={index} className="p-4 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold">{trial.nct_id}</p>
                    <p className="text-sm text-muted-foreground mt-1">{trial.title}</p>
                  </div>
                  <a
                    href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
                <div className="grid md:grid-cols-3 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Phase</p>
                    <p className="font-medium">{trial.phase}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Status</p>
                    <p className="font-medium">{trial.status}</p>
                  </div>
                  {trial.condition && (
                    <div>
                      <p className="text-xs text-muted-foreground">Condition</p>
                      <p className="font-medium">{trial.condition}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const renderLiteratureDetails = (evidence: any) => {
  return (
    <div className="space-y-6">
      {/* Literature Metrics */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">PubMed Articles</p>
          <p className="text-2xl font-bold">{evidence.article_count ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">FDA Labels</p>
          <p className="text-2xl font-bold">{evidence.drug_labels?.length ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Black Box Warnings</p>
          <p className="text-2xl font-bold">{evidence.black_box_warnings ?? 0}</p>
        </div>
        <div className="p-4 bg-muted/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Scientific Rationale</p>
          <p className="text-2xl font-bold capitalize">{evidence.scientific_rationale?.substring(0, 4) ?? 'N/A'}</p>
        </div>
      </div>

      {/* FDA Labels */}
      {evidence.drug_labels && evidence.drug_labels.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">FDA-Approved Labels</h3>
          <div className="flex flex-wrap gap-2">
            {evidence.drug_labels.map((label: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-sm py-2 px-4">
                {label}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Label Details */}
      {evidence.label_details && evidence.label_details.length > 0 && (
        <div>
          <h3 className="font-semibold mb-4">FDA Label Details ({evidence.label_details.length} labels)</h3>
          <div className="space-y-3">
            {evidence.label_details.map((label: any, index: number) => (
              <div key={index} className="p-4 bg-muted/30 rounded-lg border border-border">
                <div className="mb-2">
                  <p className="font-semibold">{label.generic_name}</p>
                  {label.brand_name && (
                    <p className="text-sm text-muted-foreground">Brand: {label.brand_name}</p>
                  )}
                </div>
                {label.indications && label.indications.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-2">Indications</p>
                    <div className="space-y-2">
                      {label.indications.map((ind: string, idx: number) => (
                        <div key={idx} className="p-3 bg-muted/20 rounded-lg border border-border w-full overflow-hidden">
                          <p className="text-sm text-foreground break-words overflow-wrap-anywhere" style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}>{ind}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {label.has_black_box_warning && (
                  <div className="mt-3 p-2 bg-amber-50/50 dark:bg-amber-950/20 rounded border border-amber-200 dark:border-amber-800">
                    <p className="text-sm text-amber-600 dark:text-amber-400 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Black box warning present
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Articles */}
      {evidence.recent_articles && evidence.recent_articles.length > 0 && (
        <div>
          <h3 className="font-semibold mb-4">Recent PubMed Articles ({evidence.recent_articles.length} articles)</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {evidence.recent_articles.map((article: any, index: number) => (
              <div key={index} className="p-4 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold">PMID: {article.pmid}</p>
                    <p className="text-sm text-muted-foreground mt-1">{article.title}</p>
                  </div>
                  <a
                    href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
                <div className="grid md:grid-cols-2 gap-4 mt-3 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Journal</p>
                    <p className="font-medium">{article.journal}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Publication Date</p>
                    <p className="font-medium">{article.publication_date}</p>
                  </div>
                  {article.authors && article.authors.length > 0 && (
                    <div className="md:col-span-2">
                      <p className="text-xs text-muted-foreground">Authors</p>
                      <p className="font-medium">{article.authors.slice(0, 5).join(', ')}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Research Summaries */}
      {evidence.research_summaries && evidence.research_summaries.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3">Research Summaries</h3>
          <div className="space-y-2">
            {evidence.research_summaries.map((summary: string, index: number) => (
              <div key={index} className="p-3 bg-muted/20 rounded-lg">
                <p className="text-sm text-foreground">{summary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Adverse Events */}
      {evidence.adverse_events && evidence.adverse_events.length > 0 && (
        <div>
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Adverse Events
          </h3>
          <div className="space-y-2">
            {evidence.adverse_events.map((event: string, index: number) => (
              <div key={index} className="p-3 bg-muted/20 rounded-lg border border-border">
                <p className="text-sm text-foreground whitespace-pre-wrap break-words">{event}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentDetails;

