"""Base agent class for all worker agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
import httpx


class BaseAgent(ABC):
    """Base class for all worker agents."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.status = "idle"
        self.progress = 0
    
    @abstractmethod
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the agent's task following the standardized contract.
        
        Args:
            session_id: Unique ID for the session
            research_topic: The research topic or query
            uploaded_paper: Data from uploaded paper (if any)
            context_data: Additional context from orchestrator
            
        Returns:
            Dictionary with standardized output:
            - status: "success" or "error"
            - data: The actual agent insights/findings
            - confidence: 0-1 confidence score
            - logs: Execution logs or breakdown
        """
        pass
    
    async def mock_api_call(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock API call with simulated delay."""
        await asyncio.sleep(0.5)  # Simulate network delay
        
        # Return mock data based on URL pattern
        if "iqvia" in url.lower() or "exim" in url.lower():
            return {
                "market_size": 2500000000,
                "cagr": 8.5,
                "competitors": ["Competitor A", "Competitor B", "Competitor C"],
                "demand_trends": "increasing",
                "geographical_hotspots": ["North America", "Europe", "Asia-Pacific"]
            }
        elif "uspto" in url.lower() or "patent" in url.lower():
            return {
                "active_patents": 12,
                "expiring_patents": 3,
                "white_space": ["Therapeutic area X", "Delivery method Y"],
                "patent_density": "moderate",
                "freedom_to_operate": True
            }
        elif "clinical" in url.lower() or "trials" in url.lower():
            return {
                "ongoing_trials": 8,
                "trial_phases": {"Phase I": 2, "Phase II": 4, "Phase III": 2},
                "gaps": ["Pediatric population", "Long-term safety"],
                "trial_failures": 2,
                "unmet_needs": ["Better efficacy", "Reduced side effects"]
            }
        elif "literature" in url.lower() or "regulatory" in url.lower():
            return {
                "drug_labels": ["FDA approved for indication X"],
                "black_box_warnings": 0,
                "adverse_events": ["Nausea", "Headache"],
                "research_summaries": ["Strong evidence for repurposing"],
                "scientific_rationale": "High"
            }
        
        return {"data": "mock_response"}
    
    def update_progress(self, progress: int):
        """Update agent progress."""
        self.progress = min(100, max(0, progress))
    
    def set_status(self, status: str):
        """Set agent status."""
        self.status = status





