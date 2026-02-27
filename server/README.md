# PharmaQuery - Backend Server

Python-based agentic AI system for pharmaceutical opportunity scouting.

## Setup

1. **Install dependencies:**
```bash
cd server
pip install -r requirements.txt
```

2. **Install Playwright browsers (required for patent scraping):**
```bash
pip install playwright
playwright install chromium
# or use the provided script:
./install_playwright.sh
```

3. **Configure Firebase (optional):**
   - Create a Firebase project at https://console.firebase.google.com
   - Generate a service account key
   - Copy `.env.example` to `.env`
   - Fill in your Firebase credentials
   - System works without Firebase (uses in-memory storage)

4. **Run the server:**
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/analyze` - Start analysis workflow
- `GET /api/status/{analysis_id}` - Get analysis status and results
- `GET /api/report/{analysis_id}` - Generate and download PDF report
- `GET /api/health` - Health check

## Architecture

- **Master Agent**: Orchestrates workflow and coordinates worker agents
- **Worker Agents**: 
  - Market Insights Agent
  - Patent Landscape Agent
  - Clinical Trials Agent
  - Regulatory & Literature Agent
- **Scoring Engine**: Combines agent outputs with weighted scores
- **Report Generator**: Creates PDF reports using ReportLab

## Database

Uses Firebase Firestore for persistent storage. Falls back to in-memory storage if Firebase is not configured.

