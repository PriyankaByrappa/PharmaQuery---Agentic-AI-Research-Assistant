export interface Opportunity {
  id: string;
  drugName: string;
  targetIndication: string;
  finalScore: number;
  marketScore: number;
  patentScore: number;
  clinicalScore: number;
  literatureScore: number;
  marketSize: string;
  cagr: string;
  patentExpiry: string;
  trialGaps: string[];
  evidence: string[];
  risks: string[];
  recommendation: string;
}

export interface AgentResult {
  agentName: string;
  status: 'idle' | 'running' | 'complete' | 'error';
  progress: number;
  insights: string[];
  data?: Record<string, unknown>;
}

export const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    drugName: 'Metformin',
    targetIndication: 'Non-Small Cell Lung Cancer',
    finalScore: 0.87,
    marketScore: 0.92,
    patentScore: 0.85,
    clinicalScore: 0.82,
    literatureScore: 0.89,
    marketSize: '$4.2B',
    cagr: '8.3%',
    patentExpiry: 'Generic Available',
    trialGaps: ['Phase III combination therapy', 'Biomarker-driven selection'],
    evidence: [
      'Strong preclinical evidence in KRAS-mutant tumors',
      '23 active clinical trials in oncology',
      'Favorable safety profile established'
    ],
    risks: ['Competition from existing therapies', 'Need for companion diagnostics'],
    recommendation: 'High Priority - Proceed with Phase II study design'
  },
  {
    id: '2',
    drugName: 'Propranolol',
    targetIndication: 'Infantile Hemangioma',
    finalScore: 0.79,
    marketScore: 0.75,
    patentScore: 0.88,
    clinicalScore: 0.78,
    literatureScore: 0.76,
    marketSize: '$890M',
    cagr: '6.1%',
    patentExpiry: 'Patent cliff 2026',
    trialGaps: ['Pediatric dosing optimization', 'Long-term follow-up studies'],
    evidence: [
      'FDA breakthrough therapy designation',
      'Orphan drug potential',
      '12 completed trials with positive outcomes'
    ],
    risks: ['Cardiovascular monitoring requirements', 'Limited patient population'],
    recommendation: 'Medium-High Priority - Expedited regulatory pathway available'
  },
  {
    id: '3',
    drugName: 'Thalidomide',
    targetIndication: 'Graft-versus-Host Disease',
    finalScore: 0.72,
    marketScore: 0.68,
    patentScore: 0.71,
    clinicalScore: 0.79,
    literatureScore: 0.70,
    marketSize: '$1.8B',
    cagr: '9.2%',
    patentExpiry: '2028',
    trialGaps: ['Chronic GVHD maintenance therapy', 'Combination with immunotherapy'],
    evidence: [
      'Established immunomodulatory mechanism',
      'Prior success in multiple myeloma',
      'Strong scientific rationale'
    ],
    risks: ['Teratogenicity concerns', 'REMS program required', 'Market competition'],
    recommendation: 'Medium Priority - Requires careful risk-benefit analysis'
  },
  {
    id: '4',
    drugName: 'Sirolimus',
    targetIndication: 'Lymphangioleiomyomatosis',
    finalScore: 0.65,
    marketScore: 0.58,
    patentScore: 0.72,
    clinicalScore: 0.68,
    literatureScore: 0.62,
    marketSize: '$450M',
    cagr: '5.4%',
    patentExpiry: '2027',
    trialGaps: ['Optimal dosing regimen', 'Patient stratification'],
    evidence: [
      'Mechanistic basis well understood',
      'Rare disease designation possible',
      '8 ongoing trials'
    ],
    risks: ['Small market size', 'Immunosuppression side effects'],
    recommendation: 'Lower Priority - Consider orphan drug strategy'
  }
];

export const mockAgentResults: Record<string, AgentResult> = {
  market: {
    agentName: 'Market Insights Agent',
    status: 'idle',
    progress: 0,
    insights: [
      'Global oncology market projected to reach $390B by 2028',
      'NSCLC segment growing at 8.3% CAGR',
      'Key competitors: Keytruda, Opdivo, Tagrisso',
      'Unmet need in KRAS-mutant populations'
    ]
  },
  patent: {
    agentName: 'Patent Landscape Agent',
    status: 'idle',
    progress: 0,
    insights: [
      'Drug substance patent expired (generic available)',
      'Formulation patents expiring 2025-2027',
      'White space identified in combination claims',
      'Freedom-to-operate confirmed for oncology use'
    ]
  },
  clinical: {
    agentName: 'Clinical Trials Agent',
    status: 'idle',
    progress: 0,
    insights: [
      '23 active trials in oncology indications',
      'Phase II data shows 34% response rate',
      'Gap: No Phase III in NSCLC combination',
      'Safety profile well-characterized'
    ]
  },
  literature: {
    agentName: 'Regulatory & Literature Agent',
    status: 'idle',
    progress: 0,
    insights: [
      '847 relevant publications identified',
      'Strong mechanistic rationale (AMPK pathway)',
      'FDA guidance available for oncology repurposing',
      'No black-box warnings relevant to indication'
    ]
  }
};
