"""Market Insights Agent - analyzes market data using Gemini AI."""
from .base_agent import BaseAgent
from .gemini_market_client import GeminiMarketClient
from typing import Dict, Any
import asyncio


class MarketAgent(BaseAgent):
    """Agent that analyzes market insights using Gemini AI."""
    
    def __init__(self):
        super().__init__("market")
        self.gemini_client = GeminiMarketClient()
    
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute market analysis using free signal-based intelligence."""
        logs = []
        try:
            self.set_status("running")
            logs.append("Started market analysis")
            self.update_progress(10)
            
            # Extract drug name and indication from query
            drug_name = self._extract_drug_name(research_topic)
            indication = self._extract_indication(research_topic)
            
            # Get data from other agents if available (from context)
            self.update_progress(20)
            clinical_data = None
            patent_data = None
            literature_data = None
            
            if context_data:
                # Try to get data from other agents in the workflow
                agent_outputs = context_data.get("agent_outputs", {})
                if "clinical" in agent_outputs:
                    # Handle new standardized output structure
                    output = agent_outputs["clinical"]
                    if output.get("status") == "success":
                        clinical_data = output.get("data", {}).get("evidence", {})
                if "patent" in agent_outputs:
                    output = agent_outputs["patent"]
                    if output.get("status") == "success":
                        patent_data = output.get("data", {}).get("evidence", {})
                if "literature" in agent_outputs:
                    output = agent_outputs["literature"]
                    if output.get("status") == "success":
                        literature_data = output.get("data", {}).get("evidence", {})
            
            # Use Gemini AI for market intelligence
            logs.append(f"Analyzing market for {drug_name}")
            self.update_progress(40)
            market_intelligence = await self.gemini_client.analyze_market_with_gemini(
                drug_name=drug_name,
                indication=indication,
                clinical_data=clinical_data,
                patent_data=patent_data,
                literature_data=literature_data
            )
            
            market_estimates = market_intelligence.get("market_estimates", {})
            
            # Process and analyze data
            self.update_progress(70)
            opportunities = self._generate_opportunities(drug_name, indication, market_estimates)
            
            self.update_progress(90)
            market_score = self._calculate_market_score(market_estimates)
            
            self.set_status("complete")
            logs.append("Market analysis complete")
            self.update_progress(100)
            
            return {
                "status": "success",
                "data": {
                    "insight_type": "market",
                    "drug_name": drug_name,
                    "indication": indication,
                    "top_opportunities": opportunities,
                    "evidence": {
                        "market_size": market_estimates.get("market_size", 0),
                        "cagr": market_estimates.get("cagr", 0),
                        "competitors": market_estimates.get("competitors", []),
                        "demand_trends": market_estimates.get("demand_trends", "unknown"),
                        "geographical_hotspots": market_estimates.get("geographical_hotspots", []),
                        "data_sources": market_intelligence.get("data_sources", []),
                        "methodology": market_estimates.get("methodology", "signal_based_estimation"),
                        "confidence": market_estimates.get("confidence", "moderate")
                    },
                    "scores": {
                        "market_potential": market_score,
                        "commercial_viability": market_score * 0.9,
                        "growth_potential": market_estimates.get("cagr", 0) / 20.0  # Normalize to 0-1
                    }
                },
                "confidence": 0.7, # Default confidence for market agent
                "logs": logs
            }
        except Exception as e:
            self.set_status("error")
            logs.append(f"Market agent error: {str(e)}")
            return {
                "status": "error",
                "data": {},
                "confidence": 0,
                "logs": logs
            }
    
    def _extract_drug_name(self, query: str) -> str:
        """Extract drug name from query."""
        # Simple extraction - can be enhanced with NLP
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
        elif "diabetes" in query_lower:
            return "Diabetes"
        return "General"
    
    def _generate_opportunities(self, drug_name: str, indication: str, 
                               market_estimates: Dict) -> list:
        """Generate market-based opportunities."""
        opportunities = []
        
        # Opportunity 1: High market size
        if market_estimates.get("market_size", 0) > 1000000000:
            opportunities.append({
                "title": f"{drug_name} for {indication} - High Market Potential",
                "description": f"Market size of ${market_estimates.get('market_size', 0):,} with {market_estimates.get('cagr', 0)}% CAGR",
                "market_size": market_estimates.get("market_size", 0),
                "cagr": market_estimates.get("cagr", 0),
                "competitors": market_estimates.get("competitors", []),
                "geographical_opportunities": market_estimates.get("geographical_hotspots", []),
                "source_agent": "market"
            })
        
        # Opportunity 2: Low competition
        if len(market_estimates.get("competitors", [])) < 3:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Low Competition",
                "description": f"Only {len(market_estimates.get('competitors', []))} major competitors identified",
                "market_size": market_estimates.get("market_size", 0) * 0.7,
                "competitive_advantage": "Low competition landscape",
                "source_agent": "market"
            })
        
        # Opportunity 3: Emerging markets
        hotspots = market_estimates.get("geographical_hotspots", [])
        if len(hotspots) > 2:
            opportunities.append({
                "title": f"{drug_name} for {indication} - Multi-Regional Opportunity",
                "description": f"Strong demand in {', '.join(hotspots)}",
                "geographical_opportunities": hotspots,
                "market_potential": "High",
                "source_agent": "market"
            })
        
        return opportunities[:3]  # Return top 3
    
    def _calculate_market_score(self, market_estimates: Dict) -> float:
        """Calculate market potential score (0-1)."""
        market_size = market_estimates.get("market_size", 0)
        cagr = market_estimates.get("cagr", 0)
        competitors = len(market_estimates.get("competitors", []))
        
        # Normalize market size (0-5B = 0-1)
        size_score = min(1.0, market_size / 5000000000)
        
        # Normalize CAGR (0-20% = 0-1)
        cagr_score = min(1.0, cagr / 20.0)
        
        # Competition score (fewer competitors = higher score)
        competition_score = max(0.0, 1.0 - (competitors / 10.0))
        
        # Weighted average
        return (size_score * 0.4 + cagr_score * 0.4 + competition_score * 0.2)

