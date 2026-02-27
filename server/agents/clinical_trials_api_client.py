"""ClinicalTrials.gov API Client for fetching real clinical trial data."""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


class ClinicalTrialsAPIClient:
    """Client for interacting with ClinicalTrials.gov API."""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    def __init__(self):
        self.timeout = 30.0
        self.rate_limit_delay = 0.5  # Delay between requests
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_trials(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search ClinicalTrials.gov for trials related to a drug and indication.
        
        Args:
            drug_name: Name of the drug
            indication: Therapeutic indication/condition
            
        Returns:
            Dictionary with API response containing studies
        """
        try:
            # Build query string
            # ClinicalTrials.gov API v2 uses query.cond parameter
            # Format: "query.cond=DRUG_NAME" or combine with condition
            query_parts = [drug_name]
            
            # Add condition if provided
            if indication:
                # Map indication to condition term
                condition_term = self._map_indication_to_condition(indication)
                # Use first condition term if multiple
                if " OR " in condition_term:
                    condition_term = condition_term.split(" OR ")[0]
                query_parts.append(condition_term)
            
            # Build final query string (space-separated)
            query_string = " ".join(query_parts)
            
            # API parameters
            params = {
                "query.cond": query_string,
                "format": "json",
                "pageSize": 100,  # Get up to 100 studies
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching clinical trials: {e}")
            return {"studies": [], "totalCount": 0}
        except Exception as e:
            print(f"Error fetching clinical trials: {e}")
            return {"studies": [], "totalCount": 0}
    
    def _normalize_phase(self, phase: str) -> str:
        """Normalize phase format from API to standard format."""
        if not phase or phase == "NA":
            return "Not Applicable"
        
        phase_upper = phase.upper()
        phase_mapping = {
            "PHASE1": "Phase I",
            "PHASE2": "Phase II",
            "PHASE3": "Phase III",
            "PHASE4": "Phase IV",
            "EARLY_PHASE1": "Early Phase I",
            "PHASE I": "Phase I",
            "PHASE II": "Phase II",
            "PHASE III": "Phase III",
            "PHASE IV": "Phase IV",
            "EARLY PHASE I": "Early Phase I"
        }
        
        return phase_mapping.get(phase_upper, phase)
    
    def _map_indication_to_condition(self, indication: str) -> str:
        """Map indication to ClinicalTrials.gov condition terms."""
        indication_lower = indication.lower()
        
        # Map common indications to condition terms (use single term for API)
        mapping = {
            "oncology": "Cancer",
            "cancer": "Cancer",
            "autoimmune": "Autoimmune Diseases",
            "autoimmune diseases": "Autoimmune Diseases",
            "anxiety": "Anxiety Disorders",
            "anxiety disorders": "Anxiety Disorders",
            "diabetes": "Diabetes Mellitus",
            "cardiovascular": "Cardiovascular Diseases",
            "cardiac": "Heart Diseases",
            "neurological": "Neurological Disorders",
            "psychiatric": "Mental Disorders"
        }
        
        for key, value in mapping.items():
            if key in indication_lower:
                return value
        
        # Return original indication if no mapping found (capitalize first letter)
        return indication.capitalize()
    
    def parse_trials_data(self, api_response: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
        """
        Parse API response into structured clinical trial data.
        
        Returns:
            Dictionary with:
            - ongoing_trials: Count of active/ongoing trials
            - trial_phases: Distribution by phase
            - gaps: Identified clinical gaps
            - trial_failures: Count of terminated/failed trials
            - unmet_needs: Unmet medical needs
            - trial_details: List of trial details
        """
        studies = api_response.get("studies", [])
        total_count = api_response.get("totalCount", len(studies))
        
        if not studies:
            return {
                "ongoing_trials": 0,
                "trial_phases": {},
                "gaps": [],
                "trial_failures": 0,
                "unmet_needs": [],
                "total_trials_found": 0,
                "trial_details": []
            }
        
        current_date = datetime.now()
        ongoing_trials = []
        trial_phases = {"Phase I": 0, "Phase II": 0, "Phase III": 0, "Phase IV": 0, "Early Phase I": 0, "Not Applicable": 0}
        terminated_trials = []
        trial_details = []
        
        for study in studies:
            try:
                protocol_section = study.get("protocolSection", {})
                identification_module = protocol_section.get("identificationModule", {})
                status_module = protocol_section.get("statusModule", {})
                design_module = protocol_section.get("designModule", {})
                conditions_module = protocol_section.get("conditionsModule", {})
                
                # Extract basic info
                nct_id = identification_module.get("nctId", "N/A")
                title = identification_module.get("briefTitle", "N/A")
                status = status_module.get("overallStatus", "Unknown")
                
                # Extract phase
                phases = design_module.get("phases", [])
                phase = phases[0] if phases else "Not Applicable"
                
                # Normalize phase format (API returns "PHASE1", "PHASE2", etc.)
                phase_normalized = self._normalize_phase(phase)
                if phase_normalized in trial_phases:
                    trial_phases[phase_normalized] += 1
                phase = phase_normalized  # Use normalized phase for trial_info
                
                # Extract conditions
                conditions = conditions_module.get("conditions", [])
                condition_text = ", ".join(conditions) if conditions else "Unknown"
                
                # Extract sponsor (for competitor identification)
                sponsor_module = protocol_section.get("sponsorCollaboratorsModule", {})
                lead_sponsor = sponsor_module.get("leadSponsor", {})
                sponsor_name = lead_sponsor.get("name", "") if lead_sponsor else ""
                
                # Extract start date
                start_date_struct = status_module.get("startDateStruct", {})
                start_date = start_date_struct.get("date", "")
                
                # Determine if trial is ongoing
                ongoing_statuses = [
                    "RECRUITING", "ACTIVE_NOT_RECRUITING", "ENROLLING_BY_INVITATION",
                    "NOT_YET_RECRUITING", "AVAILABLE"
                ]
                is_ongoing = status in ongoing_statuses
                
                # Check if terminated/failed
                is_terminated = status in ["TERMINATED", "SUSPENDED", "WITHDRAWN"]
                
                trial_info = {
                    "nct_id": nct_id,
                    "title": title,
                    "status": status,
                    "phase": phase,
                    "condition": condition_text,
                    "start_date": start_date,
                    "sponsor": sponsor_name,  # Add sponsor for competitor identification
                    "is_ongoing": is_ongoing,
                    "is_terminated": is_terminated
                }
                
                trial_details.append(trial_info)
                
                if is_ongoing:
                    ongoing_trials.append(trial_info)
                
                if is_terminated:
                    terminated_trials.append(trial_info)
                    
            except Exception as e:
                print(f"Error parsing trial: {e}")
                continue
        
        # Identify gaps
        gaps = self._identify_gaps(studies, drug_name)
        
        # Identify unmet needs
        unmet_needs = self._identify_unmet_needs(studies, ongoing_trials)
        
        return {
            "ongoing_trials": len(ongoing_trials),
            "trial_phases": {k: v for k, v in trial_phases.items() if v > 0},
            "gaps": gaps,
            "trial_failures": len(terminated_trials),
            "unmet_needs": unmet_needs,
            "total_trials_found": total_count,
            "trial_details": trial_details[:30],  # More details for in-depth view
            "ongoing_trial_details": [t for t in ongoing_trials[:20]]  # More ongoing trial details
        }
    
    def _identify_gaps(self, studies: List[Dict], drug_name: str) -> List[str]:
        """Identify clinical gaps based on trial data."""
        gaps = []
        
        # Analyze phases - if missing certain phases, that's a gap
        phases_found = set()
        for study in studies:
            design_module = study.get("protocolSection", {}).get("designModule", {})
            phases = design_module.get("phases", [])
            for phase in phases:
                normalized = self._normalize_phase(phase)
                phases_found.add(normalized)
        
        if "Phase III" not in phases_found:
            gaps.append("No Phase III trials")
        if "Phase II" not in phases_found and "Phase III" not in phases_found:
            gaps.append("Limited late-stage clinical evidence")
        
        # Analyze conditions - if few conditions, might be a gap
        conditions = set()
        for study in studies:
            conditions_module = study.get("protocolSection", {}).get("conditionsModule", {})
            study_conditions = conditions_module.get("conditions", [])
            conditions.update(study_conditions)
        
        if len(conditions) < 3:
            gaps.append("Limited indication diversity")
        
        # Analyze enrollment - if many trials are not recruiting, that's a gap
        recruiting_count = sum(1 for s in studies 
                              if s.get("protocolSection", {}).get("statusModule", {}).get("overallStatus") == "RECRUITING")
        if recruiting_count == 0:
            gaps.append("No actively recruiting trials")
        
        return gaps[:5]  # Return top 5 gaps
    
    def _identify_unmet_needs(self, studies: List[Dict], ongoing_trials: List[Dict]) -> List[str]:
        """Identify unmet medical needs based on trial data."""
        unmet_needs = []
        
        # If few ongoing trials, there's unmet need
        if len(ongoing_trials) < 3:
            unmet_needs.append("Limited active research")
        
        # If no Phase III trials, there's unmet need for late-stage evidence
        has_phase_iii = any(
            "PHASE3" in str(t.get("phase", "")).upper() 
            for t in ongoing_trials
        )
        if not has_phase_iii:
            unmet_needs.append("Need for Phase III evidence")
        
        # If many terminated trials, there's unmet need for successful trials
        terminated_count = sum(1 for s in studies 
                               if s.get("protocolSection", {}).get("statusModule", {}).get("overallStatus") in 
                               ["TERMINATED", "SUSPENDED"])
        if terminated_count > len(ongoing_trials):
            unmet_needs.append("Need for successful trial outcomes")
        
        return unmet_needs[:5]  # Return top 5

