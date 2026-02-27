/** API client for backend communication */
// In dev, Vite proxy forwards /api to backend — use empty base.
// In production, set VITE_API_URL to the backend origin.
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface QueryRequest {
  query: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  status: string;
  message: string;
}

export interface AgentStatus {
  agent_type: string;
  status: string;
  progress: number;
  insights?: string[];  // Add insights from real agent outputs
}

export interface PatentEvidence {
  active_patents?: number;
  expiring_patents?: number;
  total_patents_found?: number;
  white_space?: string[];
  patent_density?: string;
  freedom_to_operate?: boolean;
  patent_details?: Array<{
    patent_number: string;
    title: string;
    date: string;
    expiry_date: string;
    assignee: string;
    cpc_class: string[];
  }>;
  expiring_patent_details?: Array<{
    patent_number: string;
    title: string;
    expiry_date: string;
  }>;
}

export interface ClinicalEvidence {
  ongoing_trials?: number;
  total_trials_found?: number;
  trial_phases?: Record<string, number>;
  gaps?: string[];
  unmet_needs?: string[];
  trial_failures?: number;
  trial_details?: Array<{
    nct_id: string;
    title: string;
    status: string;
    phase: string;
    condition: string;
  }>;
  ongoing_trial_details?: Array<{
    nct_id: string;
    title: string;
    status: string;
    phase: string;
    condition: string;
  }>;
}

export interface LiteratureEvidence {
  drug_labels?: string[];
  black_box_warnings?: number;
  adverse_events?: string[];
  warnings?: string[];
  indications?: string[];
  research_summaries?: string[];
  scientific_rationale?: string;
  article_count?: number;
  recent_articles?: Array<{
    pmid: string;
    title: string;
    journal: string;
    publication_date: string;
    authors?: string[];
  }>;
  label_details?: Array<{
    generic_name: string;
    brand_name?: string;
    indications?: string[];
    has_black_box_warning?: boolean;
    warning_count?: number;
  }>;
}

export interface Opportunity {
  id: string;
  title: string;
  description?: string;
  scores: {
    market: number;
    patent: number;
    clinical: number;
    literature: number;
    composite: number;
  };
  justification?: string;
  pros: string[];
  cons: string[];
  risk_factors: string[];
  unmet_needs: string[];
  competitor_landscape: string[];
  patent_evidence?: PatentEvidence;
  clinical_evidence?: ClinicalEvidence;
  literature_evidence?: LiteratureEvidence;
}

export interface AgentOutput {
  evidence?: PatentEvidence | ClinicalEvidence | LiteratureEvidence | any;
  scores?: Record<string, number>;
}

export interface AnalysisStatusResponse {
  analysis_id: string;
  status: string;
  query: string;
  agents: Record<string, AgentStatus>;
  agent_outputs?: Record<string, AgentOutput>;
  opportunities?: Opportunity[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async analyzeQuery(query: string): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatusResponse> {
    const response = await fetch(`${this.baseUrl}/api/status/${analysisId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Analysis not found');
      }
      throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
  }

  async downloadReport(analysisId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/report/${analysisId}`);

    if (!response.ok) {
      throw new Error(`Failed to download report: ${response.statusText}`);
    }

    return response.blob();
  }

  // Research Specific Methods
  async uploadResearchPaper(file: File): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/research/upload`, {
      method: 'POST',
      body: formData,
      // Do NOT set Content-Type header — browser sets multipart boundary automatically
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Failed to upload paper: ${response.statusText}`);
    }

    return response.json();
  }

  async downloadResearchReport(analysisId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/research/report/${analysisId}`);

    if (!response.ok) {
      throw new Error(`Failed to download report: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research_report_${analysisId.slice(0, 8)}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  async getResearchStatus(analysisId: string): Promise<ResearchStatusResponse> {
    const response = await fetch(`${this.baseUrl}/api/research/status/${analysisId}`);

    if (response.status === 202) {
      // Analysis in progress
      return { analysis_id: analysisId, status: 'processing' } as any;
    }

    if (!response.ok) {
      throw new Error(`Failed to get research status: ${response.statusText}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }
}

export interface ResearchAnnotation {
  tag: string;
  content: string;
  tooltip?: string;
  reasoning: string;
  suggestion?: string;
  position: { start: number; end: number };
  source_name?: string;
  source_link?: string;
}

export interface ResearchOpportunity {
  id: string;
  title: string;
  source: string;
  relevance_score: number;
  difficulty_score: number;
  description: string;
  why_matched?: string;
  category?: string;
  deadline?: string;
  link: string;
}

export interface FacultyRecommendation {
  name: string;
  inst: string;
  area: string;
  why: string;
  match_score?: number;
  link: string;
}

export interface ConfidenceResult {
  level: string;
  model_certainty: number;
  data_completeness: number;
  document_clarity: number;
  signal_consistency: number;
  summary: string;
}

export interface ResearchStatusResponse {
  analysis_id: string;
  status: string;
  research_score: number;
  score_dimensions: Record<string, number>;
  annotations: ResearchAnnotation[];
  top_opportunities: ResearchOpportunity[];
  faculty_recommendations: FacultyRecommendation[];
  confidence_level: string;
  confidence_result?: ConfidenceResult;
  extracted_text?: string;
}

export const apiClient = new ApiClient();

