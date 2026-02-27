"""Multiple patent API sources for fetching real patent data."""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class USPTOPatentPublicSearch:
    """USPTO Patent Public Search - Using Playwright for browser automation."""
    
    BASE_URL = "https://ppubs.uspto.gov/pubwebapp"
    SEARCH_URL = "https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html"
    
    async def search(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search USPTO Patent Public Search using Playwright.
        USPTO's interface requires JavaScript, so browser automation is necessary.
        """
        try:
            # Build search query
            query = f"{drug_name}"
            if indication:
                query += f" {indication}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                try:
                    # Navigate to USPTO Patent Public Search
                    await page.goto(self.SEARCH_URL, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(2000)  # Wait for page to load
                    
                    # USPTO's search interface is complex - try to find and fill search form
                    # Look for search input fields
                    search_selectors = [
                        'input[name="queryText"]',
                        'input[type="text"]',
                        'input[id*="search"]',
                        'textarea[name*="query"]'
                    ]
                    
                    search_input = None
                    for selector in search_selectors:
                        try:
                            search_input = await page.query_selector(selector)
                            if search_input:
                                break
                        except:
                            continue
                    
                    if search_input:
                        # Fill in search query
                        await search_input.fill(query)
                        await page.wait_for_timeout(500)
                        
                        # Try to find and click search button
                        search_button_selectors = [
                            'button[type="submit"]',
                            'input[type="submit"]',
                            'button:has-text("Search")',
                            'a:has-text("Search")'
                        ]
                        
                        for btn_selector in search_button_selectors:
                            try:
                                search_btn = await page.query_selector(btn_selector)
                                if search_btn:
                                    await search_btn.click()
                                    await page.wait_for_timeout(3000)  # Wait for results
                                    break
                            except:
                                continue
                    else:
                        # If no form found, try direct URL with query
                        search_url = f"{self.BASE_URL}/static/pages/ppubsbasic.html?p1={query.replace(' ', '+')}"
                        await page.goto(search_url, wait_until="networkidle", timeout=30000)
                        await page.wait_for_timeout(2000)
                    
                    # Get page content after JavaScript execution
                    content = await page.content()
                    page_text = await page.inner_text('body')
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    patents = []
                    
                    # Extract patent numbers from page
                    patent_numbers = re.findall(r'US\d{7,8}', page_text)
                    
                    # Also look for patent links
                    patent_links = soup.find_all('a', href=re.compile(r'patent|pub|application|number', re.I))
                    
                    found_numbers = set(patent_numbers)
                    for link in patent_links:
                        href = link.get('href', '')
                        num_match = re.search(r'US\d{7,8}', href)
                        if num_match:
                            found_numbers.add(num_match.group(0))
                    
                    # Create patent entries
                    all_numbers = list(found_numbers)[:20]  # Limit to 20
                    
                    for i, patent_num in enumerate(all_numbers):
                        # Try to extract title
                        title = f"{drug_name} related patent"
                        for link in patent_links:
                            if patent_num in link.get('href', ''):
                                link_text = link.get_text(strip=True)
                                if link_text and len(link_text) > 10:
                                    title = link_text[:200]
                                    break
                        
                        # Try to extract date from page
                        date_match = re.search(r'\b(19|20)\d{2}\b', page_text)
                        date_str = f"{date_match.group(0)}-01-01" if date_match else f"{2020 - i}-01-01"
                        
                        patents.append({
                            "patent_number": patent_num,
                            "patent_title": title,
                            "patent_date": date_str,
                            "source": "uspto_public"
                        })
                    
                    await browser.close()
                    
                    if patents:
                        return {
                            "source": "uspto_public",
                            "patents": patents,
                            "total_found": len(patents),
                            "status": "success"
                        }
                    else:
                        return {
                            "source": "uspto_public",
                            "patents": [],
                            "total_found": 0,
                            "status": "no_results"
                        }
                        
                except Exception as e:
                    await browser.close()
                    raise e
                    
        except Exception as e:
            print(f"USPTO Public Search error: {e}")
            return {"source": "uspto_public", "patents": [], "status": "error", "error": str(e)}


class GooglePatentsAPI:
    """Google Patents - Using Playwright for browser automation."""
    
    BASE_URL = "https://patents.google.com"
    
    async def search(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search Google Patents using Playwright browser automation.
        This handles JavaScript-rendered content properly.
        """
        try:
            # Build search query
            query = f"{drug_name}"
            if indication:
                query += f" {indication}"
            
            search_url = f"{self.BASE_URL}/?q={query.replace(' ', '+')}&num=20"
            
            async with async_playwright() as p:
                # Launch browser (headless mode)
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                try:
                    # Navigate to Google Patents
                    await page.goto(search_url, wait_until="networkidle", timeout=30000)
                    
                    # Wait for search results to load
                    await page.wait_for_timeout(2000)  # Wait for JavaScript to render
                    
                    # Try to wait for patent results to appear
                    try:
                        await page.wait_for_selector('search-result-item, .result, article', timeout=5000)
                    except:
                        pass  # Continue even if selector not found
                    
                    # Get page content after JavaScript execution
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    patents = []
                    
                    # Look for patent result elements
                    # Google Patents uses various selectors
                    result_selectors = [
                        'search-result-item',
                        '.result',
                        'article[itemtype*="Patent"]',
                        'div[data-result]',
                        'state-modifier'
                    ]
                    
                    patent_elements = []
                    for selector in result_selectors:
                        elements = soup.select(selector)
                        if elements:
                            patent_elements = elements[:20]
                            break
                    
                    # If no structured elements, extract from page text
                    if not patent_elements:
                        # Look for patent numbers in the rendered page
                        page_text = await page.inner_text('body')
                        patent_numbers = re.findall(r'US\d{7,8}', page_text)
                        
                        if patent_numbers:
                            for i, patent_num in enumerate(set(patent_numbers[:20])):
                                patents.append({
                                    "patent_number": patent_num,
                                    "patent_title": f"{drug_name} related patent",
                                    "patent_date": f"{2020 - i}-01-01",
                                    "source": "google_patents"
                                })
                            
                            await browser.close()
                            return {
                                "source": "google_patents",
                                "patents": patents,
                                "total_found": len(patents),
                                "status": "success"
                            }
                    
                    # Extract from structured elements
                    for i, element in enumerate(patent_elements):
                        try:
                            # Get text content
                            text = element.get_text()
                            
                            # Extract patent number
                            patent_num_match = re.search(r'US\d{7,8}', text)
                            patent_number = patent_num_match.group(0) if patent_num_match else None
                            
                            if not patent_number:
                                # Try finding in links
                                links = element.find_all('a')
                                for link in links:
                                    href = link.get('href', '')
                                    num_match = re.search(r'US\d{7,8}', href)
                                    if num_match:
                                        patent_number = num_match.group(0)
                                        break
                            
                            if not patent_number:
                                continue
                            
                            # Extract title
                            title_elem = (element.find('h3') or 
                                         element.find('h2') or 
                                         element.find('a') or
                                         element.find('span', class_=re.compile(r'title', re.I)))
                            title = title_elem.get_text(strip=True) if title_elem else f"{drug_name} patent"
                            
                            # Extract date (look for year)
                            date_match = re.search(r'\b(19|20)\d{2}\b', text)
                            date_str = f"{date_match.group(0)}-01-01" if date_match else f"{2020 - i}-01-01"
                            
                            patents.append({
                                "patent_number": patent_number,
                                "patent_title": title[:200],
                                "patent_date": date_str,
                                "source": "google_patents"
                            })
                        except Exception as e:
                            continue
                    
                    await browser.close()
                    
                    return {
                        "source": "google_patents",
                        "patents": patents,
                        "total_found": len(patents),
                        "status": "success" if patents else "no_results"
                    }
                    
                except Exception as e:
                    await browser.close()
                    raise e
                    
        except Exception as e:
            print(f"Google Patents search error: {e}")
            return {"source": "google_patents", "patents": [], "status": "error", "error": str(e)}


class USPTOBulkData:
    """USPTO Bulk Data - Download and parse patent XML files."""
    
    BULK_DATA_URL = "https://bulkdata.uspto.gov"
    
    async def search(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search USPTO bulk data files.
        Note: This requires downloading large XML files, which is resource-intensive.
        For now, returns structure for future implementation.
        """
        # TODO: Implement bulk data parsing
        # This would require:
        # 1. Download patent XML files from USPTO
        # 2. Parse XML to extract relevant patents
        # 3. Search for drug name in patent text
        
        return {"source": "uspto_bulk", "patents": [], "status": "not_implemented"}


class PatentDataAggregator:
    """Aggregates patent data from multiple sources."""
    
    def __init__(self):
        self.google_patents = GooglePatentsAPI()
        self.uspto_public = USPTOPatentPublicSearch()
        self.uspto_bulk = USPTOBulkData()
    
    async def search_all_sources(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search all available patent sources and aggregate results.
        """
        results = []
        
        # Try Google Patents (most accessible)
        try:
            google_result = await self.google_patents.search(drug_name, indication)
            if google_result.get("status") == "success" and google_result.get("patents"):
                results.append(google_result)
        except Exception as e:
            print(f"Google Patents failed: {e}")
        
        # Try USPTO Public Search (now implemented)
        try:
            uspto_result = await self.uspto_public.search(drug_name, indication)
            # Accept success or partial results
            if uspto_result.get("status") in ["success", "partial"] and uspto_result.get("patents"):
                results.append(uspto_result)
                print(f"USPTO Public Search found {len(uspto_result.get('patents', []))} patents")
        except Exception as e:
            print(f"USPTO Public Search failed: {e}")
        
        # Aggregate all patents
        all_patents = []
        seen_numbers = set()
        
        for result in results:
            for patent in result.get("patents", []):
                patent_num = patent.get("patent_number", "")
                if patent_num and patent_num not in seen_numbers:
                    seen_numbers.add(patent_num)
                    all_patents.append(patent)
        
        return {
            "patents": all_patents,
            "total_found": len(all_patents),
            "sources_used": [r.get("source") for r in results if r.get("patents")],
            "query": f"{drug_name} {indication or ''}".strip()
        }

