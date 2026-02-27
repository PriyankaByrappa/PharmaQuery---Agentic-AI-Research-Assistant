# Clinical Trials Agent - Real API Implementation

## Overview

The Clinical Trials Agent now uses the **real ClinicalTrials.gov API v2** to fetch actual clinical trial data. No mock data fallback - returns empty results if API fails.

## API Details

- **Endpoint**: `https://clinicaltrials.gov/api/v2/studies`
- **Format**: JSON
- **Authentication**: None required (public API)
- **Rate Limits**: Be respectful, use delays between requests

## Query Format

The API uses `query.cond` parameter:
```
query.cond=DRUG_NAME CONDITION
```

Example:
```
query.cond=Metformin Cancer
```

## Implementation

### Files

1. **`clinical_trials_api_client.py`**
   - `ClinicalTrialsAPIClient` class
   - `search_trials()` - Fetches trials from API
   - `parse_trials_data()` - Parses API response into structured data
   - `_identify_gaps()` - Identifies clinical gaps
   - `_identify_unmet_needs()` - Identifies unmet medical needs

2. **`clinical_agent.py`**
   - Updated to use `ClinicalTrialsAPIClient`
   - Removed mock data fallback
   - Returns real trial data or empty structure

## Data Extracted

From each trial, we extract:
- **NCT ID**: Unique trial identifier
- **Title**: Brief title
- **Status**: Overall status (RECRUITING, COMPLETED, etc.)
- **Phase**: Trial phase (Phase I, II, III, IV, or NA)
- **Condition**: Medical condition(s) studied
- **Start Date**: Trial start date
- **Is Ongoing**: Boolean for active trials
- **Is Terminated**: Boolean for failed/terminated trials

## Aggregated Metrics

- **Ongoing Trials**: Count of active/recruiting trials
- **Trial Phases**: Distribution across phases
- **Gaps**: Identified clinical evidence gaps
- **Trial Failures**: Count of terminated/suspended trials
- **Unmet Needs**: Unmet medical needs identified
- **Total Trials Found**: Total number of trials matching query

## Status Mapping

### Ongoing Statuses
- RECRUITING
- ACTIVE_NOT_RECRUITING
- ENROLLING_BY_INVITATION
- NOT_YET_RECRUITING
- AVAILABLE

### Terminated Statuses
- TERMINATED
- SUSPENDED
- WITHDRAWN

## Gap Identification

The system automatically identifies gaps:
- Missing Phase III trials
- Limited late-stage evidence
- Limited indication diversity
- No actively recruiting trials

## Unmet Needs Identification

Identifies unmet needs based on:
- Limited active research (< 3 ongoing trials)
- Missing Phase III evidence
- High termination rate vs ongoing trials

## Error Handling

- Returns empty structure if API fails
- Handles network errors gracefully
- Uses retry logic with exponential backoff
- No mock data fallback (as requested)

## Testing

Test the implementation:
```bash
python -c "
import asyncio
from agents.clinical_agent import ClinicalAgent

async def test():
    agent = ClinicalAgent()
    result = await agent.execute('Find repurposing opportunities for Metformin in oncology')
    print(f'Ongoing trials: {result[\"evidence\"].get(\"ongoing_trials\", 0)}')
    print(f'Total trials: {result[\"evidence\"].get(\"total_trials_found\", 0)}')

asyncio.run(test())
"
```

## Notes

- **No Mock Data**: Mock data fallback has been completely removed
- API returns up to 100 studies per query
- Phase information may be "NA" for some trials (non-interventional or observational)
- All trial calculations work with real data only
- Frontend receives real clinical trial information or empty results (never mock data)





