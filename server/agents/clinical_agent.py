"""Clinical Trials Agent - analyzes trials, gaps, unmet needs."""
from .base_agent import BaseAgent
from .clinical_trials_api_client import ClinicalTrialsAPIClient
from typing import Dict, Any


class ClinicalAgent(BaseAgent):
    """Agent that analyzes clinical trials for drug repurposing opportunities."""
    
    def __init__(self):
        super().__init__("clinical")
        self.api_client = ClinicalTrialsAPIClient()
    
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute clinical trials analysis using real ClinicalTrials.gov API."""
        logs = []
        try:
            self.set_status("running")
            logs.append("Started clinical analysis")
            self.update_progress(10)
            
            drug_name = self._extract_drug_name(research_topic)
            indication = self._extract_indication(research_topic)
            
            # Fetch real clinical trials data from ClinicalTrials.gov API
            self.update_progress(20)
            try:
                logs.append(f"Searching ClinicalTrials.gov for {drug_name} and {indication}")
                api_response = await self.api_client.search_trials(drug_name, indication)
                self.update_progress(50)
                
                # Parse and analyze trial data
                trials_data = self.api_client.parse_trials_data(api_response, drug_name)
                self.update_progress(70)
            except Exception as e:
                logs.append(f"Error in clinical trials API call: {str(e)}")
                # Return empty trial data structure (no mock fallback)
                self.update_progress(50)
                trials_data = {
                    "ongoing_trials": 0,
                    "trial_phases": {},
                    "gaps": [],
                    "trial_failures": 0,
                    "unmet_needs": [],
                    "total_trials_found": 0,
                    "trial_details": [],
                    "ongoing_trial_details": []
                }
                self.update_progress(70)
            
            # Generate opportunities from real data
            self.update_progress(80)
            opportunities = self._generate_opportunities(drug_name, indication, trials_data)
            
            # Calculate scores
            self.update_progress(90)
            clinical_score = self._calculate_clinical_score(trials_data)
            
            self.set_status("complete")
            logs.append("Clinical analysis complete")
            self.update_progress(100)
            
            return {
                "status": "success",
                "data": {
                    "insight_type": "clinical",
                    "drug_name": drug_name,
                    "indication": indication,
                    "top_opportunities": opportunities,
                    "evidence": {
                        "ongoing_trials": trials_data.get("ongoing_trials", 0),
                        "trial_phases": trials_data.get("trial_phases", {}),
                        "gaps": trials_data.get("gaps", []),
                        "trial_failures": trials_data.get("trial_failures", 0),
                        "unmet_needs": trials_data.get("unmet_needs", []),
                        "total_trials_found": trials_data.get("total_trials_found", 0),
                        "trial_details": trials_data.get("trial_details", [])[:20],  # More details for in-depth view
                        "ongoing_trial_details": trials_data.get("ongoing_trial_details", [])[:15]  # More ongoing trial details
                    },
                    "scores": {
                        "clinical_score": clinical_score,
                        "trial_activity": min(1.0, trials_data.get("ongoing_trials", 0) / 10.0),
                        "gap_potential": len(trials_data.get("gaps", [])) / 5.0
                    }
                },
                "confidence": 0.75,
                "logs": logs
            }
        except Exception as e:
            self.set_status("error")
            logs.append(f"Clinical agent error: {str(e)}")
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
                               trials_data: Dict) -> list:
        """Generate clinical trial-based opportunities."""
        opportunities = []
        
        # Opportunity 1: Clinical gaps
        gaps = trials_data.get("gaps", [])
        if gaps:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Clinical Gap Opportunity",
                "description": f"Identified {len(gaps)} clinical gaps: {', '.join(gaps)}",
                "gaps": gaps,
                "rationale": "Addresses unmet clinical needs"
            })
        
        # Opportunity 2: Active trial activity
        ongoing = trials_data.get("ongoing_trials", 0)
        if ongoing > 0:
            phases = trials_data.get("trial_phases", {})
            opportunities.append({
                "title": f"{drug_name} for {indication} - Active Research",
                "description": f"{ongoing} ongoing trials across phases: {phases}",
                "ongoing_trials": ongoing,
                "trial_phases": phases,
                "momentum": "High research activity"
            })
        
        # Opportunity 3: Unmet needs
        unmet_needs = trials_data.get("unmet_needs", [])
        if unmet_needs:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Unmet Medical Needs",
                "description": f"Addresses unmet needs: {', '.join(unmet_needs)}",
                "unmet_needs": unmet_needs,
                "market_need": "High"
            })
        
        return opportunities[:3]
    
    def _calculate_clinical_score(self, trials_data: Dict) -> float:
        """Calculate clinical opportunity score (0-1)."""
        ongoing = trials_data.get("ongoing_trials", 0)
        gaps = len(trials_data.get("gaps", []))
        unmet_needs = len(trials_data.get("unmet_needs", []))
        failures = trials_data.get("trial_failures", 0)
        
        # Trial activity score (more trials = more interest)
        activity_score = min(1.0, ongoing / 10.0)
        
        # Gap score (more gaps = more opportunity)
        gap_score = min(1.0, gaps / 5.0)
        
        # Unmet needs score
        needs_score = min(1.0, unmet_needs / 5.0)
        
        # Failure score (fewer failures = better)
        failure_score = max(0.0, 1.0 - (failures / 5.0))
        
        # Weighted average
        return (activity_score * 0.3 + gap_score * 0.3 + needs_score * 0.3 + failure_score * 0.1)

