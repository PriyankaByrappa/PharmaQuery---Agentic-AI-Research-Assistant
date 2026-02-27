"""USPTO Patent API Client for fetching real patent data from multiple sources."""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from .patent_api_sources import PatentDataAggregator


class PatentAPIClient:
    """Client for interacting with USPTO patent APIs."""
    
    # USPTO Patent Public Search - Free, no API key required
    # This is a web-based search, so we'll use a simplified approach
    USPTO_SEARCH_BASE = "https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html"
    
    # Alternative: Use Google Patents API (free, but rate limited)
    # Or use USPTO bulk data files (requires downloading)
    
    # For now, we'll use a hybrid approach:
    # 1. Try to search using USPTO's public search interface
    # 2. Parse results or use structured data sources
    
    def __init__(self):
        self.timeout = 30.0
        self.rate_limit_delay = 1.0  # Delay between requests to respect rate limits
        self.aggregator = PatentDataAggregator()
    
    async def search_patents(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search for patents using HTTP-based API sources only (no browser automation).
        
        Uses the European Patent Office (EPO) Open Patent Services API
        and Google Patents via simple HTTP requests.
        """
        try:
            print(f"Searching patent APIs for: {drug_name} {indication or ''}")
            all_patents = []
            
            # Source 1: EPO Open Patent Services (free, REST API)
            try:
                epo_patents = await self._search_epo(drug_name, indication)
                all_patents.extend(epo_patents)
            except Exception as e:
                print(f"EPO search failed: {e}")
            
            # Source 2: Google Patents via simple HTTP (no Playwright)
            try:
                google_patents = await self._search_google_patents_http(drug_name, indication)
                all_patents.extend(google_patents)
            except Exception as e:
                print(f"Google Patents HTTP search failed: {e}")
            
            # Deduplicate by patent number
            seen = set()
            unique_patents = []
            for p in all_patents:
                num = p.get("patent_number", "")
                if num and num not in seen:
                    seen.add(num)
                    unique_patents.append(p)
            
            print(f"Found {len(unique_patents)} patents from HTTP APIs")
            return {
                "patents": unique_patents,
                "total_found": len(unique_patents),
                "sources_used": ["epo", "google_patents_http"],
                "query": f"{drug_name} {indication or ''}".strip()
            }
                
        except Exception as e:
            print(f"Error fetching patents: {e}")
            return {
                "patents": [],
                "total_found": 0,
                "sources_used": [],
                "query": f"{drug_name} {indication or ''}".strip(),
                "error": str(e)
            }
    
    async def _search_epo(self, drug_name: str, indication: str = None) -> List[Dict]:
        """Search European Patent Office Open Patent Services."""
        query = f"{drug_name}"
        if indication:
            query += f" {indication}"
        
        # EPO OPS REST API - published data search
        url = "https://ops.epo.org/3.2/rest-services/published-data/search"
        params = {
            "q": f'ti="{drug_name}" OR ab="{drug_name}"',
            "Range": "1-20"
        }
        
        patents = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params, headers={
                    "Accept": "application/json"
                })
                if response.status_code == 200:
                    data = response.json()
                    # Parse EPO response
                    results = data.get("ops:world-patent-data", {}).get("ops:biblio-search", {}).get("ops:search-result", {}).get("ops:publication-reference", [])
                    if isinstance(results, dict):
                        results = [results]
                    for r in results[:20]:
                        doc_id = r.get("document-id", {})
                        if isinstance(doc_id, list):
                            doc_id = doc_id[0] if doc_id else {}
                        patents.append({
                            "patent_number": doc_id.get("doc-number", {}).get("$", ""),
                            "patent_title": f"{drug_name} related patent",
                            "source": "epo"
                        })
            except Exception as e:
                print(f"EPO API error: {e}")
        
        return patents
    
    async def _search_google_patents_http(self, drug_name: str, indication: str = None) -> List[Dict]:
        """Search Google Patents using simple HTTP (no Playwright)."""
        import re as re_module
        
        query = drug_name
        if indication:
            query += f" {indication}"
        
        url = f"https://patents.google.com/?q={query.replace(' ', '+')}&num=20"
        
        patents = []
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if response.status_code == 200:
                    # Extract patent numbers from HTML
                    text = response.text
                    patent_numbers = re_module.findall(r'US\d{7,8}[A-Z]?\d*', text)
                    for pnum in list(dict.fromkeys(patent_numbers))[:20]:  # Deduplicate, take 20
                        patents.append({
                            "patent_number": pnum,
                            "patent_title": f"{drug_name} related patent",
                            "source": "google_patents"
                        })
            except Exception as e:
                print(f"Google Patents HTTP error: {e}")
        
        return patents
    
    def parse_patent_data(self, api_response: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
        """
        Parse API response into structured patent landscape data.
        
        Returns:
            Dictionary with:
            - active_patents: Count of active patents
            - expiring_patents: Count of patents expiring soon
            - patent_details: List of patent details
            - white_space: Identified white space areas
            - patent_density: Density assessment
            - freedom_to_operate: FTO assessment
        """
        # PatentsView API returns data in 'patents' field
        patents = api_response.get("patents", [])
        
        # If no patents found, return empty but valid structure
        if not patents:
            return {
                "active_patents": 0,
                "expiring_patents": 0,
                "total_patents_found": 0,
                "patent_details": [],
                "white_space": [
                    "Novel formulations and delivery methods",
                    "Combination therapies",
                    "New therapeutic indications"
                ],
                "patent_density": "none",
                "freedom_to_operate": True,
                "expiring_patent_details": []
            }
        
        current_date = datetime.now()
        expiring_threshold = current_date + timedelta(days=365 * 5)  # 5 years
        
        active_patents = []
        expiring_patents = []
        patent_details = []
        
        for patent in patents:
            patent_date_str = patent.get("patent_date", "")
            if not patent_date_str:
                # Try expiry_year if date not available
                expiry_year = patent.get("expiry_year")
                if expiry_year:
                    patent_date = datetime(expiry_year - 20, 1, 1)
                    patent_date_str = patent_date.strftime("%Y-%m-%d")
                else:
                    continue
            
            try:
                # Parse patent date (format: YYYY-MM-DD)
                if isinstance(patent_date_str, str) and len(patent_date_str) >= 10:
                    patent_date = datetime.strptime(patent_date_str[:10], "%Y-%m-%d")
                else:
                    # Fallback: use expiry_year if available
                    expiry_year = patent.get("expiry_year")
                    if expiry_year:
                        patent_date = datetime(expiry_year - 20, 1, 1)
                        patent_date_str = patent_date.strftime("%Y-%m-%d")
                    else:
                        continue
                
                # Calculate expiry (typically 20 years from filing)
                # Or use expiry_year if provided
                expiry_year = patent.get("expiry_year")
                if expiry_year:
                    expiry_date = datetime(expiry_year, 12, 31)
                else:
                    expiry_date = patent_date + timedelta(days=365 * 20)
                
                # Handle assignee (can be list or string, or missing)
                assignee_org = patent.get("assignee_organization") or patent.get("assignee")
                if isinstance(assignee_org, list) and assignee_org:
                    assignee = assignee_org[0]
                elif isinstance(assignee_org, str):
                    assignee = assignee_org
                else:
                    assignee = "Unknown"
                
                # Handle title (different field names from different sources)
                title = (patent.get("patent_title") or 
                        patent.get("title") or 
                        patent.get("patent_title", "N/A"))
                
                # Handle CPC classes (may not be available from all sources)
                cpc_classes = (patent.get("cpc_subsection_id") or 
                              patent.get("cpc_class") or 
                              [])
                if isinstance(cpc_classes, list):
                    cpc_classes = cpc_classes[:3]
                else:
                    cpc_classes = []
                
                patent_info = {
                    "patent_number": patent.get("patent_number", "N/A"),
                    "title": title,
                    "date": patent_date_str,
                    "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                    "assignee": assignee,
                    "cpc_class": cpc_classes,
                    "source": patent.get("source", "unknown")
                }
                
                patent_details.append(patent_info)
                
                # Check if patent is still active
                if expiry_date > current_date:
                    active_patents.append(patent_info)
                    
                    # Check if expiring soon
                    if expiry_date <= expiring_threshold:
                        expiring_patents.append(patent_info)
            
            except (ValueError, TypeError) as e:
                print(f"Error parsing patent date: {e}")
                continue
        
        # Analyze patent density
        patent_density = self._assess_patent_density(len(active_patents))
        
        # Assess freedom to operate
        fto = self._assess_freedom_to_operate(active_patents, expiring_patents)
        
        # Identify white space
        white_space = self._identify_white_space(patents, drug_name)
        
        return {
            "active_patents": len(active_patents),
            "expiring_patents": len(expiring_patents),
            "total_patents_found": len(patents),
            "patent_details": patent_details[:20],  # More details for in-depth view
            "white_space": white_space,
            "patent_density": patent_density,
            "freedom_to_operate": fto,
            "expiring_patent_details": [p for p in expiring_patents[:10]]  # More expiring details
        }
    
    def _assess_patent_density(self, active_count: int) -> str:
        """Assess patent density based on count."""
        if active_count == 0:
            return "none"
        elif active_count < 5:
            return "low"
        elif active_count < 15:
            return "moderate"
        else:
            return "high"
    
    def _assess_freedom_to_operate(self, active_patents: List[Dict], 
                                   expiring_patents: List[Dict]) -> bool:
        """
        Assess freedom to operate.
        FTO is better if:
        - Fewer active patents
        - More patents expiring soon
        - Patents are in different CPC classes (different use cases)
        """
        if not active_patents:
            return True  # No active patents = full FTO
        
        # If many patents expiring soon, FTO improves
        if len(expiring_patents) >= len(active_patents) * 0.3:
            return True
        
        # If very few active patents, likely FTO
        if len(active_patents) <= 3:
            return True
        
        # Otherwise, assess based on patent diversity
        # If patents cover different areas, there might be white space
        cpc_classes = set()
        for patent in active_patents:
            if patent.get("cpc_class"):
                cpc_classes.update(patent["cpc_class"])
        
        # More diverse CPC classes = more potential white space
        return len(cpc_classes) > 3
    
    def _identify_white_space(self, patents: List[Dict], drug_name: str) -> List[str]:
        """
        Identify white space opportunities.
        White space = areas with limited patent coverage.
        """
        white_space_areas = []
        
        # Analyze CPC classifications to find gaps
        cpc_coverage = set()
        for patent in patents:
            cpc_subsections = patent.get("cpc_subsection_id", [])
            cpc_coverage.update(cpc_subsections[:2])  # Top-level classifications
        
        # Common pharmaceutical CPC sections
        pharma_cpc_sections = {
            "A61K": "Preparations for medical, dental, or toilet purposes",
            "A61P": "Specific therapeutic activity of chemical compounds",
            "C07D": "Heterocyclic compounds",
            "C07C": "Acyclic or carbocyclic compounds"
        }
        
        # Find sections with limited coverage
        covered_sections = {cpc[:4] for cpc in cpc_coverage if len(cpc) >= 4}
        
        for section, description in pharma_cpc_sections.items():
            if section not in covered_sections:
                white_space_areas.append(f"{section} - {description}")
        
        # Add generic opportunities if few patents found
        if len(patents) < 5:
            white_space_areas.extend([
                "Novel formulations and delivery methods",
                "Combination therapies",
                "New therapeutic indications"
            ])
        
        return white_space_areas[:5]  # Return top 5
    
    def _get_fallback_data(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """Fallback data structure if API fails."""
        return {
            "patents": [],
            "total_found": 0
        }

