# Patent API Implementation

## Overview

The Patent Landscape Agent now uses **real USPTO patent data** via the PatentsView API.

## API Used

**PatentsView API** - Free, public API providing structured patent data
- Endpoint: `https://api.patentsview.org/patents/query`
- No API key required
- Rate limit: ~10 requests/second (we use 0.5s delay between requests)

## Features Implemented

### 1. Real Patent Search
- Searches patents by drug name in title and abstract
- Optionally filters by indication/therapeutic area
- Returns up to 100 relevant patents

### 2. Patent Analysis
- **Active Patents**: Counts patents still in force (not expired)
- **Expiring Patents**: Identifies patents expiring within 5 years
- **Patent Density**: Assesses how crowded the IP landscape is
- **Freedom to Operate (FTO)**: Determines if there's room for new patents
- **White Space**: Identifies areas with limited patent coverage

### 3. Patent Details Extracted
- Patent number
- Title
- Filing date and expiry date (20 years from filing)
- Assignee (patent owner)
- CPC classification codes

### 4. Error Handling
- Automatic retry with exponential backoff (3 attempts)
- Graceful fallback if API fails
- Rate limiting to respect API limits

## Data Flow

```
User Query → Patent Agent
    ↓
Extract drug name & indication
    ↓
Search PatentsView API
    ↓
Parse patent data
    ↓
Calculate:
  - Active patents count
  - Expiring patents
  - Patent density
  - FTO assessment
  - White space opportunities
    ↓
Return structured results
```

## Example API Query

```json
{
  "q": {
    "_or": [
      {"_text_any": {"patent_title": "Metformin"}},
      {"_text_any": {"patent_abstract": "Metformin"}}
    ]
  },
  "f": [
    "patent_number",
    "patent_title",
    "patent_date",
    "assignee_organization",
    "cpc_subsection_id"
  ],
  "o": {
    "per_page": 100,
    "page": 1
  }
}
```

## Response Structure

The agent returns:
```python
{
    "active_patents": 12,
    "expiring_patents": 3,
    "total_patents_found": 15,
    "patent_density": "moderate",
    "freedom_to_operate": True,
    "white_space": [
        "A61K - Preparations for medical purposes",
        "Novel formulations and delivery methods"
    ],
    "patent_details": [...],  # Top 10 patents
    "expiring_patent_details": [...]  # Top 5 expiring
}
```

## Testing

To test the implementation:

1. Start the backend server:
   ```bash
   cd server
   python main.py
   ```

2. Make a query from the frontend:
   - "Find repurposing opportunities for Metformin in oncology"
   - The Patent Agent will fetch real patent data

3. Check the console logs for:
   - API requests being made
   - Patent data being parsed
   - Any errors (with fallback to mock data)

## Future Enhancements

1. **USPTO Patent Public Search API**: Add as alternative/backup
2. **Patent Citation Analysis**: Analyze patent citations for deeper insights
3. **Patent Family Analysis**: Group related patents
4. **Geographic Analysis**: Filter by country/region
5. **Caching**: Cache API responses to reduce redundant calls

## Notes

- PatentsView API is free but has rate limits
- Patent expiry is calculated as 20 years from filing date
- White space identification uses CPC classification codes
- If API fails, the agent gracefully falls back to mock data





