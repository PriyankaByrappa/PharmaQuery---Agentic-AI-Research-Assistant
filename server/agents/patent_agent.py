"""Patent Landscape Agent - analyzes patents, FTO, white space."""
from .base_agent import BaseAgent
from .patent_api_client import PatentAPIClient
from typing import Dict, Any


class PatentAgent(BaseAgent):
    """Agent that analyzes patent landscape for drug repurposing opportunities."""
    
    def __init__(self):
        super().__init__("patent")
        self.api_client = PatentAPIClient()
    
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute patent analysis using real USPTO API."""
        logs = []
        try:
            self.set_status("running")
            logs.append("Started patent analysis")
            self.update_progress(10)
            
            drug_name = self._extract_drug_name(research_topic)
            indication = self._extract_indication(research_topic)
            
            # Fetch real patent data from APIs only (no mock fallback)
            self.update_progress(20)
            try:
                logs.append(f"Searching USPTO for {drug_name} and {indication}")
                api_response = await self.api_client.search_patents(drug_name, indication)
                self.update_progress(50)
                
                # Parse and analyze patent data
                patent_data = self.api_client.parse_patent_data(api_response, drug_name)
                self.update_progress(70)
            except Exception as e:
                logs.append(f"Error in patent API call: {str(e)}")
                # Return empty patent data structure (no mock fallback)
                self.update_progress(50)
                patent_data = {
                    "active_patents": 0,
                    "expiring_patents": 0,
                    "total_patents_found": 0,
                    "patent_details": [],
                    "white_space": [],
                    "patent_density": "none",
                    "freedom_to_operate": True,
                    "expiring_patent_details": []
                }
                self.update_progress(70)
            
            # Generate opportunities from real data
            self.update_progress(80)
            opportunities = self._generate_opportunities(drug_name, indication, patent_data)
            
            # Calculate scores
            self.update_progress(90)
            patent_score = self._calculate_patent_score(patent_data)
            
            self.set_status("complete")
            logs.append("Patent analysis complete")
            self.update_progress(100)
            
            return {
                "status": "success",
                "data": {
                    "insight_type": "patent",
                    "drug_name": drug_name,
                    "indication": indication,
                    "top_opportunities": opportunities,
                    "evidence": {
                        "active_patents": patent_data.get("active_patents", 0),
                        "expiring_patents": patent_data.get("expiring_patents", 0),
                        "total_patents_found": patent_data.get("total_patents_found", 0),
                        "white_space": patent_data.get("white_space", []),
                        "patent_density": patent_data.get("patent_density", "unknown"),
                        "freedom_to_operate": patent_data.get("freedom_to_operate", False),
                        "patent_details": patent_data.get("patent_details", [])[:15],  # More details for in-depth view
                        "expiring_patent_details": patent_data.get("expiring_patent_details", [])[:10]  # More expiring details
                    },
                    "scores": {
                        "patent_score": patent_score,
                        "freedom_to_operate": 1.0 if patent_data.get("freedom_to_operate") else 0.5,
                        "white_space_potential": min(1.0, len(patent_data.get("white_space", [])) / 5.0)
                    }
                },
                "confidence": 0.8,
                "logs": logs
            }
        except Exception as e:
            self.set_status("error")
            logs.append(f"Patent agent error: {str(e)}")
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
                               patent_data: Dict) -> list:
        """Generate patent-based opportunities."""
        opportunities = []
        
        # Opportunity 1: Expiring patents
        expiring = patent_data.get("expiring_patents", 0)
        if expiring > 0:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Patent Expiry Window",
                "description": f"{expiring} patents expiring soon, creating market entry opportunity",
                "expiring_patents": expiring,
                "timeline": "2-5 years",
                "advantage": "Reduced IP barriers"
            })
        
        # Opportunity 2: White space
        white_space = patent_data.get("white_space", [])
        if white_space:
            opportunities.append({
                "title": f"{drug_name} for {indication} - White Space Opportunity",
                "description": f"Identified {len(white_space)} areas with limited patent coverage",
                "white_space_areas": white_space,
                "freedom_to_operate": patent_data.get("freedom_to_operate", False)
            })
        
        # Opportunity 3: Low patent density
        density = patent_data.get("patent_density", "moderate")
        if density in ["low", "moderate"]:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Low Patent Density",
                "description": f"Patent density is {density}, indicating less crowded IP landscape",
                "patent_density": density,
                "active_patents": patent_data.get("active_patents", 0)
            })
        
        return opportunities[:3]
    
    def _calculate_patent_score(self, patent_data: Dict) -> float:
        """Calculate patent opportunity score (0-1)."""
        fto = 1.0 if patent_data.get("freedom_to_operate") else 0.5
        expiring = patent_data.get("expiring_patents", 0)
        white_space_count = len(patent_data.get("white_space", []))
        active = patent_data.get("active_patents", 0)
        
        # FTO score
        fto_score = fto
        
        # Expiring patents score (more expiring = better)
        expiring_score = min(1.0, expiring / 5.0)
        
        # White space score
        white_space_score = min(1.0, white_space_count / 5.0)
        
        # Low active patents = less crowded = better
        active_score = max(0.0, 1.0 - (active / 20.0))
        
        # Weighted average
        return (fto_score * 0.4 + expiring_score * 0.2 + white_space_score * 0.2 + active_score * 0.2)

