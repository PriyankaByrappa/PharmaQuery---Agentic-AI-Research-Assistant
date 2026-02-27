"""Regulatory & Literature Agent - analyzes drug labels, safety, scientific rationale."""
from .base_agent import BaseAgent
from .fda_api_client import FDADrugLabelingClient
from .pubmed_api_client import PubMedAPIClient
from typing import Dict, Any


class LiteratureAgent(BaseAgent):
    """Agent that analyzes regulatory and literature data for drug repurposing opportunities."""
    
    def __init__(self):
        super().__init__("literature")
        self.fda_client = FDADrugLabelingClient()
        self.pubmed_client = PubMedAPIClient()
    
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute literature and regulatory analysis using real FDA and PubMed APIs."""
        logs = []
        try:
            self.set_status("running")
            logs.append("Started literature analysis")
            self.update_progress(10)
            
            drug_name = self._extract_drug_name(research_topic)
            indication = self._extract_indication(research_topic)
            
            # Fetch real FDA drug labeling data
            self.update_progress(20)
            try:
                logs.append(f"Searching FDA labels for {drug_name}")
                fda_response = await self.fda_client.search_drug_labels(drug_name)
                self.update_progress(40)
                regulatory_data = self.fda_client.parse_drug_labels(fda_response, drug_name)
            except Exception as e:
                logs.append(f"FDA API error: {str(e)}")
                self.update_progress(40)
                regulatory_data = {
                    "drug_labels": [],
                    "black_box_warnings": 0,
                    "adverse_events": [],
                    "warnings": [],
                    "indications": [],
                    "label_details": []
                }
            
            # Fetch real PubMed literature data
            self.update_progress(50)
            try:
                logs.append(f"Searching PubMed for {drug_name} and {indication}")
                pubmed_response = await self.pubmed_client.search_literature(drug_name, indication)
                self.update_progress(70)
                literature_data = self.pubmed_client.parse_literature_data(pubmed_response, drug_name)
            except Exception as e:
                logs.append(f"PubMed API error: {str(e)}")
                self.update_progress(70)
                literature_data = {
                    "research_summaries": [],
                    "scientific_rationale": "unknown",
                    "article_count": 0,
                    "recent_articles": []
                }
            
            # Combine data
            combined_data = {**regulatory_data, **literature_data}
            
            # Generate opportunities from real data
            self.update_progress(80)
            opportunities = self._generate_opportunities(drug_name, indication, combined_data)
            
            # Calculate scores
            self.update_progress(90)
            literature_score = self._calculate_literature_score(combined_data)
            
            self.set_status("complete")
            logs.append("Literature analysis complete")
            self.update_progress(100)
            
            return {
                "status": "success",
                "data": {
                    "insight_type": "literature",
                    "drug_name": drug_name,
                    "indication": indication,
                    "top_opportunities": opportunities,
                    "evidence": {
                        "drug_labels": combined_data.get("drug_labels", []),
                        "black_box_warnings": combined_data.get("black_box_warnings", 0),
                        "adverse_events": combined_data.get("adverse_events", []),
                        "warnings": combined_data.get("warnings", []),
                        "indications": combined_data.get("indications", []),
                        "research_summaries": combined_data.get("research_summaries", []),
                        "scientific_rationale": combined_data.get("scientific_rationale", "unknown"),
                        "article_count": combined_data.get("article_count", 0),
                        "recent_articles": combined_data.get("recent_articles", [])[:10],  # More articles for in-depth view
                        "label_details": combined_data.get("label_details", [])[:10]  # More label details
                    },
                    "scores": {
                        "literature_score": literature_score,
                        "safety_score": max(0.0, 1.0 - (combined_data.get("black_box_warnings", 0) / 5.0)),
                        "scientific_rationale": 0.9 if combined_data.get("scientific_rationale") == "High" else 
                                               0.7 if combined_data.get("scientific_rationale") == "Medium" else
                                               0.4 if combined_data.get("scientific_rationale") == "Low" else 0.2
                    }
                },
                "confidence": 0.85,
                "logs": logs
            }
        except Exception as e:
            self.set_status("error")
            logs.append(f"Literature agent error: {str(e)}")
            return {
                "status": "error",
                "data": {},
                "confidence": 0,
                "logs": logs
            }
    
    def _extract_drug_name(self, query: str) -> str:
        """Extract drug name from query."""
        query_lower = query.lower()
        common_drugs = ["metformin", "thalidomide", "propranolol", "aspirin", "sildenafil"]
        for drug in common_drugs:
            if drug in query_lower:
                return drug.capitalize()
        return "Drug X"
    
    def _extract_indication(self, query: str) -> str:
        """Extract indication from query."""
        query_lower = query.lower()
        if "oncology" in query_lower or "cancer" in query_lower:
            return "Oncology"
        elif "autoimmune" in query_lower:
            return "Autoimmune Diseases"
        elif "anxiety" in query_lower:
            return "Anxiety Disorders"
        return "General"
    
    def _generate_opportunities(self, drug_name: str, indication: str, 
                               data: Dict) -> list:
        """Generate literature-based opportunities."""
        opportunities = []
        
        # Opportunity 1: Strong scientific rationale
        rationale = data.get("scientific_rationale", "unknown")
        if rationale == "High":
            opportunities.append({
                "title": f"{drug_name} for {indication} - Strong Scientific Basis",
                "description": "High scientific rationale supported by literature",
                "scientific_rationale": rationale,
                "research_summaries": data.get("research_summaries", []),
                "strength": "Strong"
            })
        
        # Opportunity 2: Favorable safety profile
        black_box = data.get("black_box_warnings", 0)
        if black_box == 0:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Favorable Safety Profile",
                "description": "No black box warnings, well-established safety profile",
                "black_box_warnings": black_box,
                "adverse_events": data.get("adverse_events", []),
                "safety": "Favorable"
            })
        
        # Opportunity 3: Existing regulatory approval
        labels = data.get("drug_labels", [])
        if labels:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Regulatory Foundation",
                "description": f"FDA approved for related indications: {', '.join(labels)}",
                "drug_labels": labels,
                "regulatory_status": "Approved",
                "advantage": "Existing regulatory pathway"
            })
        
        return opportunities[:3]
    
    def _calculate_literature_score(self, data: Dict) -> float:
        """Calculate literature/regulatory opportunity score (0-1)."""
        rationale = data.get("scientific_rationale", "unknown")
        black_box = data.get("black_box_warnings", 0)
        research_count = len(data.get("research_summaries", []))
        labels = len(data.get("drug_labels", []))
        
        # Rationale score
        rationale_score = 0.9 if rationale == "High" else 0.6 if rationale == "Medium" else 0.3
        
        # Safety score (fewer warnings = better)
        safety_score = max(0.0, 1.0 - (black_box / 5.0))
        
        # Research support score
        research_score = min(1.0, research_count / 5.0)
        
        # Regulatory foundation score
        regulatory_score = min(1.0, labels / 3.0)
        
        # Weighted average
        return (rationale_score * 0.4 + safety_score * 0.3 + research_score * 0.2 + regulatory_score * 0.1)

