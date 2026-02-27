# PharmaQuery - Agentic AI System

An end-to-end agentic AI system for pharmaceutical opportunity scouting that analyzes drug repurposing opportunities using multiple specialized agents.

## Architecture Overview

The system follows an 8-stage workflow:

1. **User Input** - User enters query via web dashboard
2. **Master Agent** - Interprets query and orchestrates workflow
3. **Worker Agents** - Run in parallel:
   - Market Insights Agent (IQVIA/EXIM data)
   - Patent Landscape Agent (USPTO data)
   - Clinical Trials Agent (ClinicalTrials.gov data)
   - Regulatory & Literature Agent (FDA/literature data)
4. **Agent Outputs** - Structured JSON stored in Firebase
5. **Master Aggregation** - Combines all agent insights
6. **Scoring Engine** - Weighted composite scoring
7. **Ranked Opportunities** - Displayed in dashboard
8. **PDF Report** - Generated using ReportLab

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - REST API framework
- **Firebase Firestore** - Database
- **ReportLab** - PDF generation
- **asyncio** - Parallel agent execution

### Frontend
- **React + TypeScript**
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components

## Setup Instructions

### Backend Setup

1. Navigate to server directory:
```bash
cd server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Firebase:
   - Create a Firebase project at https://console.firebase.google.com
   - Generate a service account key
   - Copy `.env.example` to `.env`
   - Fill in your Firebase credentials

4. Run the server:
```bash
python main.py
# or
./run.sh
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Configure API URL (optional):
   - Copy `.env.example` to `.env`
   - Update `VITE_API_URL` if backend is on different port

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## API Endpoints

- `POST /api/analyze` - Start analysis workflow
  - Body: `{ "query": "Find repurposing opportunities for Drug X in oncology" }`
  - Returns: `{ "analysis_id": "...", "status": "processing" }`

- `GET /api/status/{analysis_id}` - Get analysis status and results
  - Returns: Analysis status, agent progress, and ranked opportunities

- `GET /api/report/{analysis_id}` - Download PDF report
  - Returns: PDF file

- `GET /api/health` - Health check

## Usage Example

1. Start both backend and frontend servers
2. Open the dashboard in your browser
3. Enter a query like: "Find repurposing opportunities for Metformin in oncology"
4. Watch the agents execute in parallel
5. View ranked opportunities with scores
6. Download comprehensive PDF report

## Scoring Model

Composite score calculation:
```
Final Score = 0.3 × Market + 0.25 × Patent + 0.25 × Clinical + 0.2 × Literature
```

Weights are configurable in `server/config.py`

## Project Structure

```
PharmaQuery/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   └── lib/            # Utilities and API client
│   └── package.json
├── server/                 # Python backend
│   ├── agents/             # Agent implementations
│   │   ├── master_agent.py
│   │   ├── market_agent.py
│   │   ├── patent_agent.py
│   │   ├── clinical_agent.py
│   │   └── literature_agent.py
│   ├── database.py         # Firebase integration
│   ├── scoring_engine.py   # Scoring logic
│   ├── report_generator.py # PDF generation
│   └── main.py             # FastAPI app
└── README.md
```

## Development Notes

- Agents use mock APIs by default (can be replaced with real APIs)
- Firebase is optional - system falls back to in-memory storage if not configured
- All agent outputs are stored in Firebase for persistence
- PDF reports are saved in `server/reports/` directory

## License

MIT




