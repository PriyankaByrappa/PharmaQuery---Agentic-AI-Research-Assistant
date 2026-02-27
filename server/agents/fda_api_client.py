"""FDA Drug Labeling API Client for fetching real regulatory data."""
import httpx
from typing import Dict, Any, List, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


class FDADrugLabelingClient:
    """Client for interacting with FDA Drug Labeling API."""
    
    BASE_URL = "https://api.fda.gov/drug/label.json"
    
    def __init__(self):
        self.timeout = 30.0
        self.rate_limit_delay = 0.5  # Delay between requests
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_drug_labels(self, drug_name: str) -> Dict[str, Any]:
        """
        Search FDA Drug Labeling API for drug information.
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Dictionary with API response containing drug labels
        """
        try:
            # FDA API uses search parameter to query drug labels
            # Try multiple search strategies
            # First try: simple search across all fields
            search_query = drug_name.lower()
            
            params = {
                "search": search_query,
                "limit": 10  # Get up to 10 labels
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching FDA drug labels: {e}")
            return {"results": []}
        except Exception as e:
            print(f"Error fetching FDA drug labels: {e}")
            return {"results": []}
    
    def parse_drug_labels(self, api_response: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
        """
        Parse API response into structured drug labeling data.
        
        Returns:
            Dictionary with:
            - drug_labels: List of approved indications
            - black_box_warnings: Count of black box warnings
            - adverse_events: List of common adverse events
            - warnings: List of warnings
            - indications: List of indications
        """
        results = api_response.get("results", [])
        
        if not results:
            return {
                "drug_labels": [],
                "black_box_warnings": 0,
                "adverse_events": [],
                "warnings": [],
                "indications": [],
                "label_details": []
            }
        
        drug_labels = []
        black_box_warnings = 0
        adverse_events = []
        warnings = []
        indications = []
        label_details = []
        
        for label in results:
            try:
                # Extract openfda data
                openfda = label.get("openfda", {})
                generic_name = openfda.get("generic_name", [drug_name])[0] if openfda.get("generic_name") else drug_name
                brand_name = openfda.get("brand_name", [""])[0] if openfda.get("brand_name") else ""
                
                # Extract indications
                label_data = label.get("indications_and_usage", [])
                if label_data:
                    for indication_text in label_data:
                        if indication_text and indication_text not in indications:
                            # Keep full text, but clean it up
                            cleaned_text = indication_text.strip()
                            if cleaned_text:
                                indications.append(cleaned_text)
                
                # Extract warnings (including black box)
                warnings_data = label.get("warnings", [])
                boxed_warnings = label.get("boxed_warnings", [])
                
                if boxed_warnings:
                    black_box_warnings += len(boxed_warnings)
                    for warning in boxed_warnings:
                        if warning and warning not in warnings:
                            warnings.append(warning[:200])
                
                if warnings_data:
                    for warning in warnings_data:
                        if warning and warning not in warnings:
                            warnings.append(warning[:200])
                
                # Extract adverse events
                adverse_reactions = label.get("adverse_reactions", [])
                if adverse_reactions:
                    for reaction in adverse_reactions:
                        if reaction:
                            cleaned_reaction = reaction.strip()
                            if cleaned_reaction and cleaned_reaction not in adverse_events:
                                adverse_events.append(cleaned_reaction)
                
                # Create label summary
                label_summary = f"{brand_name} ({generic_name})" if brand_name else generic_name
                if label_summary not in drug_labels:
                    drug_labels.append(label_summary)
                
                # Store detailed label info with all indications for this specific label
                label_indications = []
                if label_data:
                    for indication_text in label_data:
                        if indication_text:
                            cleaned_text = indication_text.strip()
                            if cleaned_text and cleaned_text not in label_indications:
                                label_indications.append(cleaned_text)
                
                label_details.append({
                    "generic_name": generic_name,
                    "brand_name": brand_name,
                    "indications": label_indications,  # All indications for this label
                    "has_black_box_warning": len(boxed_warnings) > 0,
                    "warning_count": len(warnings_data) + len(boxed_warnings)
                })
                
            except Exception as e:
                print(f"Error parsing FDA label: {e}")
                continue
        
        return {
            "drug_labels": drug_labels[:5],  # Top 5
            "black_box_warnings": black_box_warnings,
            "adverse_events": adverse_events[:10],  # Top 10
            "warnings": warnings[:5],  # Top 5
            "indications": indications[:5],  # Top 5
            "label_details": label_details[:10]  # More label details for in-depth view
        }

