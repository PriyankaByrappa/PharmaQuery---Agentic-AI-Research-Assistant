"""PubMed E-utilities API Client for fetching scientific literature."""
import httpx
from typing import Dict, Any, List, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import xml.etree.ElementTree as ET


class PubMedAPIClient:
    """Client for interacting with PubMed E-utilities API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.timeout = 30.0
        self.rate_limit_delay = 0.5  # Delay between requests (PubMed allows 3 requests/sec without key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_literature(self, drug_name: str, indication: str = None) -> Dict[str, Any]:
        """
        Search PubMed for literature related to drug and indication.
        
        Args:
            drug_name: Name of the drug
            indication: Therapeutic indication/condition
            
        Returns:
            Dictionary with search results including PubMed IDs
        """
        try:
            # Build search query
            query = f"{drug_name}[Title/Abstract]"
            if indication:
                query += f" AND {indication}[Title/Abstract]"
            
            # Step 1: Search PubMed using esearch
            esearch_url = f"{self.BASE_URL}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": 20,  # Get up to 20 articles
                "sort": "relevance"  # Sort by relevance
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                response = await client.get(esearch_url, params=params)
                response.raise_for_status()
                search_result = response.json()
                
                # Extract PubMed IDs
                id_list = search_result.get("esearchresult", {}).get("idlist", [])
                total_count = int(search_result.get("esearchresult", {}).get("count", 0))
                
                if not id_list:
                    return {
                        "pmids": [],
                        "total_count": 0,
                        "articles": []
                    }
                
                # Step 2: Fetch article details using efetch
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                articles = await self._fetch_article_details(client, id_list)
                
                return {
                    "pmids": id_list,
                    "total_count": total_count,
                    "articles": articles
                }
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching PubMed literature: {e}")
            return {"pmids": [], "total_count": 0, "articles": []}
        except Exception as e:
            print(f"Error fetching PubMed literature: {e}")
            return {"pmids": [], "total_count": 0, "articles": []}
    
    async def _fetch_article_details(self, client: httpx.AsyncClient, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed article information using efetch."""
        try:
            if not pmids:
                return []
            
            # Join PubMed IDs
            id_string = ",".join(pmids[:20])  # Limit to 20 articles
            
            efetch_url = f"{self.BASE_URL}/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": id_string,
                "retmode": "xml"
            }
            
            response = await client.get(efetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            articles = []
            
            # Parse each article
            for article in root.findall(".//PubmedArticle"):
                try:
                    # Extract title
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "N/A"
                    
                    # Extract abstract
                    abstract_elems = article.findall(".//AbstractText")
                    abstract = ""
                    if abstract_elems:
                        abstract = " ".join([elem.text or "" for elem in abstract_elems])
                    
                    # Extract authors
                    author_list = article.find(".//AuthorList")
                    authors = []
                    if author_list is not None:
                        for author in author_list.findall(".//Author"):
                            last_name = author.find("LastName")
                            first_name = author.find("ForeName")
                            if last_name is not None:
                                author_name = last_name.text or ""
                                if first_name is not None:
                                    author_name += f", {first_name.text or ''}"
                                authors.append(author_name)
                    
                    # Extract publication date
                    pub_date_elem = article.find(".//PubDate")
                    pub_date = "N/A"
                    if pub_date_elem is not None:
                        year_elem = pub_date_elem.find("Year")
                        if year_elem is not None:
                            pub_date = year_elem.text or "N/A"
                    
                    # Extract journal
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "N/A"
                    
                    # Extract PubMed ID
                    pmid_elem = article.find(".//MedlineCitation/PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "N/A"
                    
                    articles.append({
                        "pmid": pmid,
                        "title": title[:300],  # Limit title length
                        "abstract": abstract[:500],  # Limit abstract length
                        "authors": authors[:5],  # Top 5 authors
                        "journal": journal[:100],
                        "publication_date": pub_date
                    })
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error fetching article details: {e}")
            return []
    
    def parse_literature_data(self, api_response: Dict[str, Any], drug_name: str) -> Dict[str, Any]:
        """
        Parse API response into structured literature data.
        
        Returns:
            Dictionary with:
            - research_summaries: List of research summaries
            - scientific_rationale: Assessment of scientific rationale
            - article_count: Number of articles found
            - recent_articles: List of recent articles
        """
        articles = api_response.get("articles", [])
        total_count = api_response.get("total_count", len(articles))
        
        if not articles:
            return {
                "research_summaries": [],
                "scientific_rationale": "unknown",
                "article_count": 0,
                "recent_articles": []
            }
        
        # Generate research summaries from article titles and abstracts
        research_summaries = []
        for article in articles[:5]:  # Top 5 articles
            title = article.get("title", "")
            abstract = article.get("abstract", "")
            if title:
                summary = f"{title}"
                if abstract:
                    summary += f": {abstract[:200]}..."
                research_summaries.append(summary)
        
        # Assess scientific rationale based on article count and recency
        article_count = len(articles)
        if article_count >= 10:
            scientific_rationale = "High"
        elif article_count >= 5:
            scientific_rationale = "Medium"
        elif article_count >= 1:
            scientific_rationale = "Low"
        else:
            scientific_rationale = "unknown"
        
        return {
            "research_summaries": research_summaries,
            "scientific_rationale": scientific_rationale,
            "article_count": total_count,
            "recent_articles": articles[:15],  # More articles for in-depth view
            "all_articles": articles  # All articles for detailed analysis
        }

