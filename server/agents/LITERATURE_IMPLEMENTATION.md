# Regulatory & Literature Agent - Real API Implementation

## Overview

The Regulatory & Literature Agent now uses **real FDA Drug Labeling API** and **PubMed E-utilities API** to fetch actual regulatory and scientific literature data. No mock data fallback - returns empty results if APIs fail.

## API Details

### 1. FDA Drug Labeling API

- **Endpoint**: `https://api.fda.gov/drug/label.json`
- **Format**: JSON
- **Authentication**: None required (public API)
- **Rate Limits**: Be respectful, use delays between requests
- **Query Format**: Simple search across all fields
  ```
  search=DRUG_NAME
  ```

### 2. PubMed E-utilities API

- **Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
- **Format**: JSON (esearch) and XML (efetch)
- **Authentication**: None required (public API)
- **Rate Limits**: 3 requests per second without API key
- **Query Format**: 
  ```
  term=DRUG_NAME[Title/Abstract] AND INDICATION[Title/Abstract]
  ```

## Implementation

### Files

1. **`fda_api_client.py`**
   - `FDADrugLabelingClient` class
   - `search_drug_labels()` - Fetches drug labels from FDA API
   - `parse_drug_labels()` - Parses API response into structured data

2. **`pubmed_api_client.py`**
   - `PubMedAPIClient` class
   - `search_literature()` - Searches PubMed and fetches article details
   - `_fetch_article_details()` - Fetches detailed article information
   - `parse_literature_data()` - Parses API response into structured data

3. **`literature_agent.py`**
   - Updated to use both `FDADrugLabelingClient` and `PubMedAPIClient`
   - Removed mock data fallback
   - Returns real regulatory and literature data or empty structure

## Data Extracted

### FDA Drug Labels

From each label, we extract:
- **Generic Name**: Drug's generic name
- **Brand Name**: Brand name(s)
- **Indications**: Approved indications for use
- **Black Box Warnings**: Count of boxed warnings
- **Warnings**: List of warnings and precautions
- **Adverse Events**: Common adverse reactions

### PubMed Articles

From each article, we extract:
- **PubMed ID (PMID)**: Unique article identifier
- **Title**: Article title
- **Abstract**: Article abstract
- **Authors**: List of authors
- **Journal**: Publication journal
- **Publication Date**: Year of publication

## Aggregated Metrics

- **Drug Labels**: List of approved drug labels
- **Black Box Warnings**: Count of black box warnings
- **Adverse Events**: List of common adverse events
- **Research Summaries**: Summaries from top articles
- **Scientific Rationale**: Assessment (High/Medium/Low/unknown)
- **Article Count**: Total number of articles found

## Scientific Rationale Assessment

Based on article count:
- **High**: ≥10 articles
- **Medium**: 5-9 articles
- **Low**: 1-4 articles
- **unknown**: 0 articles

## Error Handling

- Returns empty structure if APIs fail
- Handles network errors gracefully
- Uses retry logic with exponential backoff
- No mock data fallback (as requested)

## Testing

Test the implementation:
```bash
python -c "
import asyncio
from agents.literature_agent import LiteratureAgent

async def test():
    agent = LiteratureAgent()
    result = await agent.execute('Find repurposing opportunities for Metformin in oncology')
    print(f'Drug labels: {len(result[\"evidence\"].get(\"drug_labels\", []))}')
    print(f'Article count: {result[\"evidence\"].get(\"article_count\", 0)}')
    print(f'Scientific rationale: {result[\"evidence\"].get(\"scientific_rationale\", \"unknown\")}')

asyncio.run(test())
"
```

## Notes

- **No Mock Data**: Mock data fallback has been completely removed
- FDA API searches across all fields (generic_name, brand_name, active_ingredient, etc.)
- PubMed API uses two-step process: esearch to find articles, then efetch to get details
- All regulatory and literature calculations work with real data only
- Frontend receives real regulatory and literature information or empty results (never mock data)





