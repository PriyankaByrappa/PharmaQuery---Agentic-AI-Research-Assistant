import { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Navbar } from '@/components/landing/Navbar';
import { QueryInput } from '@/components/dashboard/QueryInput';
import { MasterAgentVisualization } from '@/components/dashboard/MasterAgentVisualization';
import { AgentCard } from '@/components/dashboard/AgentCard';
import { OpportunityCard } from '@/components/dashboard/OpportunityCard';
import { AgentOutputCard } from '@/components/dashboard/AgentOutputCard';
import { ScoringPanel } from '@/components/dashboard/ScoringPanel';
import { Button } from '@/components/ui/button';
import { Download, RotateCcw } from 'lucide-react';
import { apiClient, type Opportunity, type AgentStatus, type AgentOutput } from '@/lib/api';
import { toast } from 'sonner';

type MasterStatus = 'idle' | 'orchestrating' | 'aggregating' | 'complete';

const Dashboard = () => {
  const location = useLocation();
  const [masterStatus, setMasterStatus] = useState<MasterStatus>('idle');
  const [currentQuery, setCurrentQuery] = useState('');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [agentResults, setAgentResults] = useState<Record<string, { agentName: string; status: 'idle' | 'running' | 'complete' | 'error'; progress: number; insights: string[] }>>({
    market: { agentName: 'Market Insights Agent', status: 'idle', progress: 0, insights: [] },
    patent: { agentName: 'Patent Landscape Agent', status: 'idle', progress: 0, insights: [] },
    clinical: { agentName: 'Clinical Trials Agent', status: 'idle', progress: 0, insights: [] },
    literature: { agentName: 'Regulatory & Literature Agent', status: 'idle', progress: 0, insights: [] }
  });
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [agentOutputs, setAgentOutputs] = useState<Record<string, AgentOutput>>({});
  const [showResults, setShowResults] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRestoredRef = useRef(false);

  // Restore scroll position immediately on mount if returning from AgentDetails
  useLayoutEffect(() => {
    const state = location.state as { analysisId?: string; preserveState?: boolean } | null;
    const savedScrollPosition = sessionStorage.getItem('dashboardScrollPosition');

    if (state?.preserveState && savedScrollPosition) {
      const scrollPosition = parseInt(savedScrollPosition, 10);
      // Set scroll position immediately, synchronously before browser paint
      window.scrollTo(0, scrollPosition);
      scrollRestoredRef.current = true;
    }
  }, [location.state]);

  // Restore state when returning from AgentDetails
  useEffect(() => {
    const state = location.state as { analysisId?: string; preserveState?: boolean } | null;
    if (state?.preserveState && state.analysisId) {
      // Restore the analysis state
      setAnalysisId(state.analysisId);
      restoreAnalysisState(state.analysisId);
    }
  }, [location.state]);

  // Ensure scroll position is maintained after content renders (in case content height changes)
  useEffect(() => {
    const savedScrollPosition = sessionStorage.getItem('dashboardScrollPosition');
    if (!savedScrollPosition || !scrollRestoredRef.current) return;

    const agentOutputsCount = Object.keys(agentOutputs).length;
    const hasContent = showResults && (opportunities.length > 0 || agentOutputsCount > 0);

    if (hasContent) {
      // Re-apply scroll position after content renders to ensure it's correct
      const scrollPosition = parseInt(savedScrollPosition, 10);
      // Use a small delay to ensure layout is complete
      const timeoutId = setTimeout(() => {
        window.scrollTo({
          top: scrollPosition,
          behavior: 'instant' as ScrollBehavior
        });
        // Clear the saved position after restoring
        sessionStorage.removeItem('dashboardScrollPosition');
        scrollRestoredRef.current = false;
      }, 50);

      return () => clearTimeout(timeoutId);
    }
  }, [showResults, opportunities.length, Object.keys(agentOutputs).length]);

  const restoreAnalysisState = async (id: string): Promise<void> => {
    try {
      const status = await apiClient.getAnalysisStatus(id);

      if (status.status === 'complete') {
        setMasterStatus('complete');
        setShowResults(true);
        setCurrentQuery(status.query || '');

        if (status.opportunities) {
          setOpportunities(status.opportunities);
        }
        if (status.agent_outputs) {
          setAgentOutputs(status.agent_outputs);
        }

        // Restore agent statuses
        const updatedAgents: Record<string, { agentName: string; status: 'idle' | 'running' | 'complete' | 'error'; progress: number; insights: string[] }> = {};
        for (const [key, agentStatus] of Object.entries(status.agents)) {
          updatedAgents[key] = {
            agentName: agentStatus.agent_type === 'market' ? 'Market Insights Agent' :
              agentStatus.agent_type === 'patent' ? 'Patent Landscape Agent' :
                agentStatus.agent_type === 'clinical' ? 'Clinical Trials Agent' :
                  'Regulatory & Literature Agent',
            status: agentStatus.status as 'idle' | 'running' | 'complete' | 'error',
            progress: agentStatus.progress,
            insights: agentStatus.insights || []
          };
        }
        setAgentResults(updatedAgents);
      }
    } catch (error) {
      console.error('Error restoring analysis state:', error);
    }
  };

  const pollAnalysisStatus = async (id: string) => {
    try {
      const status = await apiClient.getAnalysisStatus(id);

      // Update master status
      if (status.status === 'processing') {
        setMasterStatus('orchestrating');
      } else if (status.status === 'complete') {
        setMasterStatus('complete');
        setShowResults(true);
        setIsLoading(false);
        if (status.opportunities) {
          setOpportunities(status.opportunities);
          toast.success(`Analysis complete! Found ${status.opportunities.length} repurposing opportunities.`);
        }
        if (status.agent_outputs) {
          setAgentOutputs(status.agent_outputs);
        }
      } else if (status.status === 'error') {
        setMasterStatus('idle');
        setIsLoading(false);
        toast.error('Analysis failed. Please try again.');
        return;
      }

      // Update agent statuses with real insights from API
      const updatedAgents: Record<string, { agentName: string; status: 'idle' | 'running' | 'complete' | 'error'; progress: number; insights: string[] }> = {};
      for (const [key, agentStatus] of Object.entries(status.agents)) {
        updatedAgents[key] = {
          agentName: agentStatus.agent_type === 'market' ? 'Market Insights Agent' :
            agentStatus.agent_type === 'patent' ? 'Patent Landscape Agent' :
              agentStatus.agent_type === 'clinical' ? 'Clinical Trials Agent' :
                'Regulatory & Literature Agent',
          status: agentStatus.status as 'idle' | 'running' | 'complete' | 'error',
          progress: agentStatus.progress,
          insights: agentStatus.insights || [] // Use real insights from API
        };
      }
      setAgentResults(prev => ({ ...prev, ...updatedAgents }));

      // Continue polling if still processing
      if (status.status === 'processing') {
        setTimeout(() => pollAnalysisStatus(id), 2000);
      }
    } catch (error) {
      console.error('Error polling status:', error);
      setIsLoading(false);
      toast.error('Failed to check analysis status');
    }
  };

  const runAnalysis = async (query: string) => {
    setIsLoading(true);
    setCurrentQuery(query);
    setShowResults(false);
    setOpportunities([]);

    // Reset agents
    setAgentResults({
      market: { agentName: 'Market Insights Agent', status: 'idle', progress: 0, insights: [] },
      patent: { agentName: 'Patent Landscape Agent', status: 'idle', progress: 0, insights: [] },
      clinical: { agentName: 'Clinical Trials Agent', status: 'idle', progress: 0, insights: [] },
      literature: { agentName: 'Regulatory & Literature Agent', status: 'idle', progress: 0, insights: [] }
    });

    try {
      // Start analysis
      setMasterStatus('orchestrating');
      const response = await apiClient.analyzeQuery(query);
      setAnalysisId(response.analysis_id);

      // Start polling for status
      setTimeout(() => pollAnalysisStatus(response.analysis_id), 1000);
    } catch (error) {
      console.error('Error starting analysis:', error);
      setIsLoading(false);
      setMasterStatus('idle');
      toast.error('Failed to start analysis. Please check if the backend server is running.');
    }
  };

  const handleReset = () => {
    setMasterStatus('idle');
    setCurrentQuery('');
    setShowResults(false);
    setAnalysisId(null);
    setOpportunities([]);
    setAgentOutputs({});
    setAgentResults({
      market: { agentName: 'Market Insights Agent', status: 'idle', progress: 0, insights: [] },
      patent: { agentName: 'Patent Landscape Agent', status: 'idle', progress: 0, insights: [] },
      clinical: { agentName: 'Clinical Trials Agent', status: 'idle', progress: 0, insights: [] },
      literature: { agentName: 'Regulatory & Literature Agent', status: 'idle', progress: 0, insights: [] }
    });
    setIsLoading(false);
  };

  const handleExportAll = async () => {
    if (!analysisId) {
      toast.error('No analysis to export');
      return;
    }

    try {
      toast.info('Generating PDF report...');
      const blob = await apiClient.downloadReport(analysisId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `pharma_query_report_${analysisId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error('Failed to download report');
    }
  };

  return (
    <>
      <Helmet>
        <title>Dashboard - PharmaQuery</title>
        <meta name="description" content="Analyze drug repurposing opportunities with our multi-agent AI system." />
      </Helmet>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="pt-20 pb-12">
          <div className="container px-4 md:px-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">Analysis Dashboard</h1>
                <p className="text-muted-foreground mt-1">Multi-agent drug repurposing intelligence</p>
              </div>
              {showResults && (
                <div className="flex gap-3">
                  <Button variant="outline" onClick={handleReset}>
                    <RotateCcw className="mr-2 h-4 w-4" />
                    New Analysis
                  </Button>
                  <Button onClick={handleExportAll}>
                    <Download className="mr-2 h-4 w-4" />
                    Export All
                  </Button>
                </div>
              )}
            </div>

            {/* Query Input */}
            <QueryInput onSubmit={runAnalysis} isLoading={isLoading} />

            {/* Agent Workflow Section */}
            {masterStatus !== 'idle' && (
              <div className="mt-8">
                <h2 className="text-lg font-semibold mb-4">Agent Workflow</h2>

                <div className="grid lg:grid-cols-3 gap-6">
                  {/* Master Agent */}
                  <div className="lg:col-span-1">
                    <MasterAgentVisualization status={masterStatus} query={currentQuery} />
                    {showResults && <div className="mt-4"><ScoringPanel /></div>}
                  </div>

                  {/* Worker Agents */}
                  <div className="lg:col-span-2">
                    <div className="grid sm:grid-cols-2 gap-4">
                      <AgentCard type="market" result={agentResults.market} />
                      <AgentCard type="patent" result={agentResults.patent} />
                      <AgentCard type="clinical" result={agentResults.clinical} />
                      <AgentCard type="literature" result={agentResults.literature} />
                    </div>

                    {/* Pros and Cons - Under the 4 agent cards */}
                    {showResults && opportunities.length > 0 && (() => {
                      // Aggregate unique pros and cons from all opportunities
                      // Use Map to track and deduplicate (handles exact matches)
                      const prosMap = new Map<string, string>();
                      const consMap = new Map<string, string>();
                      const risksMap = new Map<string, string>();

                      opportunities.forEach(opp => {
                        opp.pros?.forEach(pro => {
                          const normalized = pro.trim();
                          if (normalized && !prosMap.has(normalized)) {
                            prosMap.set(normalized, normalized);
                          }
                        });
                        opp.cons?.forEach(con => {
                          const normalized = con.trim();
                          if (normalized && !consMap.has(normalized)) {
                            consMap.set(normalized, normalized);
                          }
                        });
                        opp.risk_factors?.forEach(risk => {
                          const normalized = risk.trim();
                          if (normalized && !risksMap.has(normalized)) {
                            risksMap.set(normalized, normalized);
                          }
                        });
                      });

                      const allPros = Array.from(prosMap.values());
                      const allCons = Array.from(consMap.values());
                      const allRisks = Array.from(risksMap.values());

                      return (
                        <div className="mt-6 grid md:grid-cols-2 gap-4 pt-6 border-t border-border">
                          {/* Pros */}
                          {allPros.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-sm flex items-center gap-2 mb-3">
                                <span className="text-emerald-500">✓</span>
                                Pros
                              </h4>
                              <ul className="space-y-2">
                                {allPros.map((item, index) => (
                                  <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2 flex-shrink-0" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Cons & Risks */}
                          {(allCons.length > 0 || allRisks.length > 0) && (
                            <div>
                              <h4 className="font-semibold text-sm flex items-center gap-2 mb-3">
                                <span className="text-amber-500">⚠</span>
                                Cons & Risk Factors
                              </h4>
                              <ul className="space-y-2">
                                {allCons.map((item, index) => (
                                  <li key={`cons-${index}`} className="text-sm text-muted-foreground flex items-start gap-2">
                                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                                    {item}
                                  </li>
                                ))}
                                {allRisks.map((item, index) => (
                                  <li key={`risk-${index}`} className="text-sm text-muted-foreground flex items-start gap-2">
                                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                </div>
              </div>
            )}

            {/* Agent Outputs Section */}
            {showResults && Object.keys(agentOutputs).length > 0 && (
              <div className="mt-12">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold">Agent Outputs</h2>
                  <p className="text-muted-foreground text-sm mt-1">
                    Detailed outputs from all four analysis agents
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {Object.entries(agentResults).map(([agentType, agentResult]) => {
                    const output = agentOutputs[agentType as keyof typeof agentOutputs];
                    const scores = output?.scores || {};
                    // Get the primary score for each agent type
                    let score: number | undefined;
                    if (agentType === 'market') {
                      score = scores.market_potential;
                    } else if (agentType === 'patent') {
                      score = scores.patent_score;
                    } else if (agentType === 'clinical') {
                      score = scores.clinical_score;
                    } else if (agentType === 'literature') {
                      score = scores.literature_score;
                    }

                    return (
                      <AgentOutputCard
                        key={agentType}
                        agentType={agentType as 'market' | 'patent' | 'clinical' | 'literature'}
                        agentStatus={{
                          agent_type: agentType,
                          status: agentResult.status,
                          progress: agentResult.progress,
                          insights: agentResult.insights
                        }}
                        evidence={output?.evidence}
                        score={score}
                        analysisId={analysisId || undefined}
                      />
                    );
                  })}
                </div>
              </div>
            )}

            {/* Results Section */}
            {showResults && (
              <div className="mt-12">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-semibold">Ranked Opportunities</h2>
                    <p className="text-muted-foreground text-sm mt-1">
                      Sorted by composite score based on market, patent, clinical, and literature analysis
                    </p>
                  </div>
                </div>

                <div className="grid gap-6">
                  {opportunities.length > 0 ? (
                    opportunities.map((opportunity, index) => (
                      <OpportunityCard
                        key={opportunity.id}
                        opportunity={opportunity}
                        rank={index + 1}
                      />
                    ))
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      No opportunities found
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
};

export default Dashboard;
