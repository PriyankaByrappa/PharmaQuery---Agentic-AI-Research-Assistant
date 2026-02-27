"""Gemini AI Market Intelligence Client - uses Google Gemini to analyze market data."""
import httpx
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiMarketClient:
    """Client for using Gemini AI to generate market insights."""
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.timeout = 60.0
    
    async def analyze_market_with_gemini(self, drug_name: str, indication: str,
                                         clinical_data: Dict = None,
                                         patent_data: Dict = None,
                                         literature_data: Dict = None) -> Dict[str, Any]:
        """
        Use Gemini AI to analyze market signals and generate insights.
        """
        if not self.api_key:
            print("[Gemini] No API key found, falling back to signal-based estimation")
            return await self._fallback_analysis(drug_name, indication, clinical_data, patent_data, literature_data)
        
        # Prepare context for Gemini
        context = self._prepare_context(drug_name, indication, clinical_data, patent_data, literature_data)
        
        # Create prompt for Gemini
        prompt = self._create_market_analysis_prompt(context)
        
        try:
            # Call Gemini API
            response = await self._call_gemini(prompt)
            
            # Parse Gemini response
            market_insights = self._parse_gemini_response(response)
            
            return {
                "signals": context.get("signals", {}),
                "market_estimates": market_insights,
                "data_sources": ["gemini_ai", "clinical_trials", "patents", "literature"],
                "methodology": "gemini_ai_analysis"
            }
        except Exception as e:
            print(f"[Gemini] Error calling Gemini API: {e}")
            return await self._fallback_analysis(drug_name, indication, clinical_data, patent_data, literature_data)
    
    def _prepare_context(self, drug_name: str, indication: str,
                         clinical_data: Dict, patent_data: Dict, literature_data: Dict) -> Dict[str, Any]:
        """Prepare context data for Gemini analysis."""
        context = {
            "drug_name": drug_name,
            "indication": indication,
            "signals": {}
        }
        
        # Clinical trial signals
        if clinical_data:
            context["signals"]["trial_activity"] = {
                "ongoing_trials": clinical_data.get("ongoing_trials", 0),
                "total_trials": clinical_data.get("total_trials_found", 0),
                "trial_phases": clinical_data.get("trial_phases", {}),
                "gaps": clinical_data.get("gaps", [])
            }
            
            # Extract trial sponsors for competitor identification
            trial_details = clinical_data.get("trial_details", [])
            sponsors = []
            for trial in trial_details:
                sponsor = trial.get("sponsor", "")
                if sponsor and sponsor.lower() not in ["unknown", "n/a", ""]:
                    sponsors.append(sponsor)
            context["signals"]["trial_sponsors"] = list(set(sponsors))[:10]
        
        # Patent signals
        if patent_data:
            context["signals"]["patent_activity"] = {
                "active_patents": patent_data.get("active_patents", 0),
                "expiring_patents": patent_data.get("expiring_patents", 0),
                "total_patents": patent_data.get("total_patents_found", 0),
                "freedom_to_operate": patent_data.get("freedom_to_operate", False)
            }
            
            # Extract patent assignees for competitor identification
            patent_details = patent_data.get("patent_details", [])
            assignees = []
            for patent in patent_details:
                assignee = patent.get("assignee", "")
                if assignee and assignee.lower() not in ["unknown", "n/a", ""]:
                    assignees.append(assignee)
            context["signals"]["patent_assignees"] = list(set(assignees))[:10]
        
        # Literature signals
        if literature_data:
            context["signals"]["research_activity"] = {
                "article_count": literature_data.get("article_count", 0),
                "scientific_rationale": literature_data.get("scientific_rationale", "unknown"),
                "fda_labels": len(literature_data.get("drug_labels", []))
            }
        
        return context
    
    def _create_market_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for Gemini to analyze market data."""
        drug_name = context["drug_name"]
        indication = context["indication"]
        signals = context["signals"]
        
        prompt = f"""You are a pharmaceutical market intelligence analyst. Analyze the following data and provide market insights for {drug_name} in {indication}.

**Available Data:**
"""
        
        if signals.get("trial_activity"):
            trial = signals["trial_activity"]
            prompt += f"""
- Clinical Trials: {trial.get('ongoing_trials', 0)} ongoing, {trial.get('total_trials', 0)} total
- Trial Phases: {trial.get('trial_phases', {})}
- Trial Sponsors: {', '.join(signals.get('trial_sponsors', [])) if signals.get('trial_sponsors') else 'Not available'}
"""
        
        if signals.get("patent_activity"):
            patent = signals["patent_activity"]
            prompt += f"""
- Patents: {patent.get('active_patents', 0)} active, {patent.get('expiring_patents', 0)} expiring
- Patent Assignees: {', '.join(signals.get('patent_assignees', [])) if signals.get('patent_assignees') else 'Not available'}
- Freedom to Operate: {patent.get('freedom_to_operate', False)}
"""
        
        if signals.get("research_activity"):
            research = signals["research_activity"]
            prompt += f"""
- Research: {research.get('article_count', 0)} PubMed articles
- Scientific Rationale: {research.get('scientific_rationale', 'unknown')}
- FDA Labels: {research.get('fda_labels', 0)}
"""
        
        prompt += f"""

**Your Task:**
Based on this data, provide a JSON response with the following structure:
{{
  "market_size_usd": <estimated market size in USD, e.g., 2500000000 for $2.5B>,
  "cagr_percent": <estimated CAGR percentage, e.g., 8.5>,
  "competitors": [<list of 3-5 real pharmaceutical company names that are actual competitors in this space, extracted from patent assignees and trial sponsors if available, otherwise use realistic major pharma companies for this therapeutic area>],
  "demand_trends": "<increasing/stable/decreasing/strongly_increasing>",
  "geographical_hotspots": [<list of 2-3 regions, e.g., "North America", "Europe", "Asia-Pacific">],
  "market_rationale": "<brief explanation of market opportunity>"
}}

**Important:**
- Use REAL company names from patent assignees and trial sponsors when available
- If no real competitors found, use realistic major pharma companies active in {indication}
- NEVER use generic names like "Competitor A", "Competitor B", "Competitor C"
- Market size should be realistic based on indication prevalence and trial activity
- CAGR should reflect growth trends in the therapeutic area
- Competitors should be actual pharmaceutical companies, not generic placeholders

Return ONLY valid JSON, no additional text.
"""
        
        return prompt
    
    async def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API."""
        url = f"{self.GEMINI_API_URL}?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    
    def _parse_gemini_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gemini API response."""
        try:
            # Extract text from Gemini response
            candidates = response.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in Gemini response")
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise ValueError("No parts in Gemini response")
            
            text = parts[0].get("text", "")
            
            # Try to extract JSON from the response
            # Gemini might wrap JSON in markdown code blocks
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            elif "```" in text:
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            
            # Parse JSON
            market_data = json.loads(text)
            
            # Validate and structure response
            return {
                "market_size": market_data.get("market_size_usd", 1000000000),
                "cagr": market_data.get("cagr_percent", 5.0),
                "competitors": market_data.get("competitors", []),
                "demand_trends": market_data.get("demand_trends", "stable"),
                "geographical_hotspots": market_data.get("geographical_hotspots", ["North America", "Europe"]),
                "market_rationale": market_data.get("market_rationale", ""),
                "confidence": "high",  # Gemini analysis
                "methodology": "gemini_ai_analysis"
            }
        except Exception as e:
            print(f"[Gemini] Error parsing response: {e}")
            print(f"[Gemini] Response text: {text[:500] if 'text' in locals() else 'N/A'}")
            raise
    
    async def _fallback_analysis(self, drug_name: str, indication: str,
                                clinical_data: Dict, patent_data: Dict, literature_data: Dict) -> Dict[str, Any]:
        """Fallback to signal-based analysis if Gemini fails."""
        from .market_intelligence_client import MarketIntelligenceClient
        fallback_client = MarketIntelligenceClient()
        return await fallback_client.analyze_market_signals(
            drug_name, indication, clinical_data, patent_data, literature_data
        )

