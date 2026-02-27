import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Shield, 
  FlaskConical, 
  BookOpen,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle,
  Download,
  FileText
} from 'lucide-react';
import type { Opportunity } from '@/lib/api';
import { useState } from 'react';

interface OpportunityCardProps {
  opportunity: Opportunity;
  rank: number;
}

export const OpportunityCard = ({ opportunity, rank }: OpportunityCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-emerald-500';
    if (score >= 0.6) return 'text-amber-500';
    return 'text-muted-foreground';
  };

  const getScoreBg = (score: number) => {
    if (score >= 0.8) return 'bg-emerald-500';
    if (score >= 0.6) return 'bg-amber-500';
    return 'bg-muted';
  };

  const getRankBadge = () => {
    if (rank === 1) return 'bg-amber-500 text-amber-950';
    if (rank === 2) return 'bg-slate-400 text-slate-950';
    if (rank === 3) return 'bg-amber-700 text-amber-100';
    return 'bg-muted text-muted-foreground';
  };

  return (
    <div className="bg-card border border-border overflow-hidden">
      {/* Header */}
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className={cn("w-8 h-8 flex items-center justify-center text-sm font-bold", getRankBadge())}>
              #{rank}
            </span>
            <div>
              <h3 className="font-semibold text-lg">{opportunity.title}</h3>
              {opportunity.description && (
                <p className="text-sm text-muted-foreground">{opportunity.description}</p>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className={cn("text-2xl font-bold", getScoreColor(opportunity.scores.composite))}>
              {(opportunity.scores.composite * 100).toFixed(0)}
            </div>
            <p className="text-xs text-muted-foreground">Overall Score</p>
          </div>
        </div>

        {/* Score breakdown */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="text-center p-2 bg-muted/30">
            <TrendingUp className="h-4 w-4 mx-auto mb-1 text-emerald-500" />
            <div className="text-sm font-semibold">{(opportunity.scores.market * 100).toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">Market</div>
          </div>
          <div className="text-center p-2 bg-muted/30">
            <Shield className="h-4 w-4 mx-auto mb-1 text-blue-500" />
            <div className="text-sm font-semibold">{(opportunity.scores.patent * 100).toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">Patent</div>
          </div>
          <div className="text-center p-2 bg-muted/30">
            <FlaskConical className="h-4 w-4 mx-auto mb-1 text-purple-500" />
            <div className="text-sm font-semibold">{(opportunity.scores.clinical * 100).toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">Clinical</div>
          </div>
          <div className="text-center p-2 bg-muted/30">
            <BookOpen className="h-4 w-4 mx-auto mb-1 text-amber-500" />
            <div className="text-sm font-semibold">{(opportunity.scores.literature * 100).toFixed(0)}</div>
            <div className="text-xs text-muted-foreground">Literature</div>
          </div>
        </div>

        {/* Justification */}
        {opportunity.justification && (
          <div className="mb-4">
            <p className="text-sm text-muted-foreground">{opportunity.justification}</p>
          </div>
        )}

        {/* Score bar */}
        <Progress value={opportunity.scores.composite * 100} className={cn("h-2", getScoreBg(opportunity.scores.composite))} />

        {/* Expand button */}
        <Button
          variant="ghost"
          size="sm"
          className="w-full mt-4"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <>Hide Details <ChevronUp className="ml-2 h-4 w-4" /></>
          ) : (
            <>View Details <ChevronDown className="ml-2 h-4 w-4" /></>
          )}
        </Button>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="border-t border-border p-5 bg-muted/20">
          {/* Unmet Needs */}
          {opportunity.unmet_needs && opportunity.unmet_needs.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-sm mb-3">Unmet Needs</h4>
              <div className="flex flex-wrap gap-2">
                {opportunity.unmet_needs.map((need, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {need}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Competitor Landscape */}
          {opportunity.competitor_landscape && opportunity.competitor_landscape.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold text-sm mb-3">Competitor Landscape</h4>
              <div className="flex flex-wrap gap-2">
                {opportunity.competitor_landscape.map((competitor, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {competitor}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Patent Evidence */}
          {opportunity.patent_evidence && (
            <div className="mt-6">
              <h4 className="font-semibold text-sm flex items-center gap-2 mb-3">
                <Shield className="h-4 w-4 text-blue-500" />
                Patent Landscape Details
              </h4>
              <div className="grid md:grid-cols-2 gap-4 p-4 bg-blue-50/50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Active Patents</p>
                  <p className="text-sm font-semibold">{opportunity.patent_evidence.active_patents ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Expiring Patents (within 5 years)</p>
                  <p className="text-sm font-semibold">{opportunity.patent_evidence.expiring_patents ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Total Patents Found</p>
                  <p className="text-sm font-semibold">{opportunity.patent_evidence.total_patents_found ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Patent Density</p>
                  <p className="text-sm font-semibold capitalize">{opportunity.patent_evidence.patent_density ?? 'unknown'}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Freedom to Operate</p>
                  <p className="text-sm font-semibold">{opportunity.patent_evidence.freedom_to_operate ? 'Yes' : 'No'}</p>
                </div>
              </div>
              
              {/* White Space */}
              {opportunity.patent_evidence.white_space && opportunity.patent_evidence.white_space.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">White Space Opportunities</p>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.patent_evidence.white_space.map((space, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {space}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Patent Details - Show more for patent opportunities */}
              {opportunity.patent_evidence.patent_details && opportunity.patent_evidence.patent_details.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Patent Details ({opportunity.patent_evidence.patent_details.length} patents)</p>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {opportunity.patent_evidence.patent_details.map((patent, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="font-medium">{patent.patent_number}</p>
                        <p className="text-muted-foreground">{patent.title}</p>
                        <div className="flex gap-4 mt-1 text-muted-foreground">
                          <span>Filed: {patent.date}</span>
                          <span>Expires: {patent.expiry_date}</span>
                        </div>
                        {patent.assignee && <p className="text-muted-foreground mt-1">Assignee: {patent.assignee}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Expiring Patent Details - Show more for patent opportunities */}
              {opportunity.patent_evidence.expiring_patent_details && opportunity.patent_evidence.expiring_patent_details.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Expiring Patents (within 5 years) ({opportunity.patent_evidence.expiring_patent_details.length} patents)</p>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {opportunity.patent_evidence.expiring_patent_details.map((patent, index) => (
                      <div key={index} className="text-xs p-2 bg-amber-50/50 dark:bg-amber-950/20 rounded border border-amber-200 dark:border-amber-800">
                        <p className="font-medium">{patent.patent_number}</p>
                        <p className="text-muted-foreground">{patent.title}</p>
                        <div className="flex gap-4 mt-1 text-muted-foreground">
                          <span>Filed: {patent.date}</span>
                          <span>Expires: {patent.expiry_date}</span>
                        </div>
                        {patent.assignee && <p className="text-muted-foreground mt-1">Assignee: {patent.assignee}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Clinical Evidence */}
          {opportunity.clinical_evidence && (
            <div className="mt-6">
              <h4 className="font-semibold text-sm flex items-center gap-2 mb-3">
                <FlaskConical className="h-4 w-4 text-purple-500" />
                Clinical Trials Data
              </h4>
              <div className="grid md:grid-cols-2 gap-4 p-4 bg-purple-50/50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Ongoing Trials</p>
                  <p className="text-sm font-semibold">{opportunity.clinical_evidence.ongoing_trials ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Total Trials Found</p>
                  <p className="text-sm font-semibold">{opportunity.clinical_evidence.total_trials_found ?? 0}</p>
                </div>
                {opportunity.clinical_evidence.trial_phases && Object.keys(opportunity.clinical_evidence.trial_phases).length > 0 && (
                  <div className="md:col-span-2">
                    <p className="text-xs text-muted-foreground mb-2">Trial Phases</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(opportunity.clinical_evidence.trial_phases).map(([phase, count]) => (
                        <Badge key={phase} variant="secondary" className="text-xs">
                          {phase}: {count}
                        </Badge>
                      ))}
            </div>
                  </div>
                )}
          </div>

              {opportunity.clinical_evidence.gaps && opportunity.clinical_evidence.gaps.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Clinical Gaps</p>
            <div className="flex flex-wrap gap-2">
                    {opportunity.clinical_evidence.gaps.map((gap, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                  {gap}
                </Badge>
              ))}
            </div>
          </div>
              )}
              
              {/* Ongoing Trial Details - Show more for clinical opportunities */}
              {opportunity.clinical_evidence.ongoing_trial_details && opportunity.clinical_evidence.ongoing_trial_details.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Ongoing Trials ({opportunity.clinical_evidence.ongoing_trial_details.length} trials)</p>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {opportunity.clinical_evidence.ongoing_trial_details.map((trial, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="font-medium">{trial.nct_id}</p>
                        <p className="text-muted-foreground">{trial.title}</p>
                        <div className="flex gap-4 mt-1 text-muted-foreground">
                          <span>Phase: {trial.phase}</span>
                          <span>Status: {trial.status}</span>
                        </div>
                        {trial.condition && <p className="text-muted-foreground mt-1">Condition: {trial.condition}</p>}
                        {trial.start_date && <p className="text-muted-foreground">Started: {trial.start_date}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Trial Details - Show more if no ongoing trials */}
              {opportunity.clinical_evidence.trial_details && opportunity.clinical_evidence.trial_details.length > 0 && 
               (!opportunity.clinical_evidence.ongoing_trial_details || opportunity.clinical_evidence.ongoing_trial_details.length === 0) && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Trial Details ({opportunity.clinical_evidence.trial_details.length} trials)</p>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {opportunity.clinical_evidence.trial_details.map((trial, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="font-medium">{trial.nct_id}</p>
                        <p className="text-muted-foreground">{trial.title}</p>
                        <div className="flex gap-4 mt-1 text-muted-foreground">
                          <span>Phase: {trial.phase}</span>
                          <span>Status: {trial.status}</span>
                        </div>
                        {trial.condition && <p className="text-muted-foreground mt-1">Condition: {trial.condition}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Literature Evidence */}
          {opportunity.literature_evidence && (
            <div className="mt-6">
              <h4 className="font-semibold text-sm flex items-center gap-2 mb-3">
                <BookOpen className="h-4 w-4 text-amber-500" />
                Regulatory & Literature Data
              </h4>
              <div className="grid md:grid-cols-2 gap-4 p-4 bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">PubMed Articles</p>
                  <p className="text-sm font-semibold">{opportunity.literature_evidence.article_count ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">FDA Labels</p>
                  <p className="text-sm font-semibold">{opportunity.literature_evidence.drug_labels?.length ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Black Box Warnings</p>
                  <p className="text-sm font-semibold">{opportunity.literature_evidence.black_box_warnings ?? 0}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Scientific Rationale</p>
                  <p className="text-sm font-semibold capitalize">{opportunity.literature_evidence.scientific_rationale ?? 'unknown'}</p>
                </div>
          </div>
              
              {opportunity.literature_evidence.drug_labels && opportunity.literature_evidence.drug_labels.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">FDA-Approved Labels</p>
                  <div className="flex flex-wrap gap-2">
                    {opportunity.literature_evidence.drug_labels.map((label, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {label}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {opportunity.literature_evidence.research_summaries && opportunity.literature_evidence.research_summaries.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Research Summaries</p>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {opportunity.literature_evidence.research_summaries.slice(0, 3).map((summary, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="text-muted-foreground">{summary}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Recent Articles - Show more for literature opportunities */}
              {opportunity.literature_evidence.recent_articles && opportunity.literature_evidence.recent_articles.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">Recent PubMed Articles ({opportunity.literature_evidence.recent_articles.length} articles)</p>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {opportunity.literature_evidence.recent_articles.map((article, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="font-medium">PMID: {article.pmid}</p>
                        <p className="text-muted-foreground">{article.title}</p>
                        <div className="flex gap-4 mt-1 text-muted-foreground">
                          <span>{article.journal}</span>
                          <span>{article.publication_date}</span>
                        </div>
                        {article.authors && article.authors.length > 0 && (
                          <p className="text-muted-foreground mt-1">Authors: {article.authors.slice(0, 3).join(', ')}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Label Details */}
              {opportunity.literature_evidence.label_details && opportunity.literature_evidence.label_details.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">FDA Label Details</p>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {opportunity.literature_evidence.label_details.map((label, index) => (
                      <div key={index} className="text-xs p-2 bg-muted/50 rounded">
                        <p className="font-medium">{label.generic_name}</p>
                        {label.brand_name && <p className="text-muted-foreground">Brand: {label.brand_name}</p>}
                        {label.indications && label.indications.length > 0 && (
                          <p className="text-muted-foreground mt-1">Indications: {label.indications.join(', ')}</p>
                        )}
                        {label.has_black_box_warning && (
                          <p className="text-amber-600 dark:text-amber-400 mt-1">⚠️ Black box warning present</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Justification */}
          {opportunity.justification && (
            <div className="mt-6 p-4 bg-primary/5 border border-primary/20">
              <h4 className="font-semibold text-sm mb-2">Justification</h4>
              <p className="text-sm text-foreground">{opportunity.justification}</p>
            </div>
          )}

          {/* Action button */}
          <div className="mt-6 flex justify-end">
            <Button size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
