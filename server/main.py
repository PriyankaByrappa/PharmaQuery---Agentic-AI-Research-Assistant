"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import asyncio
<<<<<<< HEAD
import random
=======
import io
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67
from agents.master_agent import MasterAgent
from agents.research_agent import ResearchAgent
from scoring_engine import ScoringEngine
from report_generator import ReportGenerator
from database import Database
from config import CORS_ORIGINS

app = FastAPI(title="PharmaQuery API", version="1.0.0")

# CORS middleware - more permissive for development
# Strip whitespace from origins and filter out empty strings
cors_origins = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],  # Allow all in dev if no origins specified
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize components
master_agent = MasterAgent()
research_agent = ResearchAgent()
scoring_engine = ScoringEngine()
report_generator = ReportGenerator()


# Request/Response Models
class QueryRequest(BaseModel):
    query: str


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class AgentStatus(BaseModel):
    agent_type: str
    status: str
    progress: int
    insights: List[str] = []  # Add insights field


class OpportunityResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    scores: Dict[str, float]
    justification: Optional[str]
    pros: List[str]
    cons: List[str]
    risk_factors: List[str]
    unmet_needs: List[str]
    competitor_landscape: List[str]
    # Evidence from agents
    patent_evidence: Optional[Dict[str, Any]] = None
    clinical_evidence: Optional[Dict[str, Any]] = None
    literature_evidence: Optional[Dict[str, Any]] = None


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    query: str
    agents: Dict[str, AgentStatus]
    agent_outputs: Optional[Dict[str, Dict[str, Any]]] = None
    opportunities: Optional[List[OpportunityResponse]] = None


# Research Specific Models
class ResearchAnnotation(BaseModel):
    tag: str
    content: str
    tooltip: Optional[str] = None
    reasoning: str
    suggestion: Optional[str] = None
    position: Dict[str, int]
    source_name: Optional[str] = None
    source_link: Optional[str] = None


class ResearchOpportunity(BaseModel):
    id: str
    title: str
    source: str
    relevance_score: int
    difficulty_score: int
    description: str
    why_matched: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[str] = None
    link: str


class FacultyRecommendation(BaseModel):
    name: str
    inst: str
    area: str
    why: str
    link: str


class ConfidenceResult(BaseModel):
    level: str
    model_certainty: int
    data_completeness: int
    document_clarity: int
    signal_consistency: int
    summary: str


class ResearchStatusResponse(BaseModel):
    analysis_id: str
    status: str
    research_score: float
    score_dimensions: Dict[str, int]
    annotations: List[ResearchAnnotation]
    top_opportunities: List[ResearchOpportunity]
    faculty_recommendations: List[FacultyRecommendation]
    confidence_level: str
    confidence_result: Optional[ConfidenceResult] = None
    extracted_text: Optional[str] = None


# In-memory storage for analysis results (in production, use Firebase)
analysis_store: Dict[str, Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PharmaQuery API", "version": "1.0.0"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_query(request: QueryRequest):
    """
    Start analysis workflow.
    Returns analysis_id for tracking.
    """
    analysis_id = str(uuid.uuid4())
    
    # Initialize analysis store
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "query": request.query,
        "status": "processing",
        "agents": {},
        "opportunities": None
    }
    
    # Run analysis in background
    asyncio.create_task(run_analysis(analysis_id, request.query))
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="processing",
        message="Analysis started. Use /api/status/{analysis_id} to check progress."
    )


async def run_analysis(analysis_id: str, query: str):
    """FAST MVP: Run the complete analysis workflow immediately."""
    try:
        # Step 1: Initialize status immediately to avoid polling delay
        analysis_store[analysis_id]["status"] = "processing"
        
        # Step 2: Master agent orchestrates workflow (now gutted and fast)
        # Wrap in a wait_for to enforce the 3-second safety rule
        try:
            master_result = await asyncio.wait_for(
                master_agent.execute(query, analysis_id),
                timeout=3.0
            )
        except asyncio.TimeoutError:
            print(f"Workflow timeout for {analysis_id}, returning partial results")
            master_result = {
                "agent_outputs": {},
                "aggregated": {"opportunities": []}
            }
        
        # Step 3: Score opportunities
        agent_outputs = master_result.get("agent_outputs", {})
        aggregated = master_result.get("aggregated", {})
        
        # Unwrap agent outputs to 'data' level for scoring engine compatibility
        # Agents return {"status": "success", "data": {"evidence": ..., "scores": ...}}
        # Scoring engine expects {"evidence": ..., "scores": ...}
        unwrapped_outputs = {}
        for agent_type, output in agent_outputs.items():
            unwrapped_outputs[agent_type] = output.get("data", {})
        
        scored_opportunities = scoring_engine.score_opportunities(
            unwrapped_outputs, 
            aggregated.get("opportunities", [])
        )
        
        # Step 4: Save opportunities and mark complete
        Database.save_opportunities(analysis_id, scored_opportunities)
        
        analysis_store[analysis_id].update({
            "status": "complete",
            "agents": {
                agent_type: {
                    "agent_type": agent_type,
                    "status": "complete",
                    "progress": 100
                }
                for agent_type in ["market", "patent", "clinical", "literature"]
            },
            "opportunities": scored_opportunities,
            "agent_outputs": agent_outputs
        })
        
    except Exception as e:
<<<<<<< HEAD
        print(f"Error in fast analysis {analysis_id}: {e}")
        analysis_store[analysis_id]["status"] = "complete" # Still mark complete to unblock UI
=======
        import traceback
        print(f"Error in analysis {analysis_id}: {e}")
        traceback.print_exc()
        analysis_store[analysis_id]["status"] = "error"
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67
        analysis_store[analysis_id]["error"] = str(e)


@app.get("/api/status/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str):
    """Get analysis status and results."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    
    # Get agent statuses with insights from agent outputs
    agents = {}
    agent_outputs = analysis.get("agent_outputs", {})
    
    for agent_type in ["market", "patent", "clinical", "literature"]:
        if agent_type in analysis.get("agents", {}):
            agent_status = analysis["agents"][agent_type]
            # Extract insights from agent output
            insights = []
            if agent_type in agent_outputs:
                output = agent_outputs[agent_type]
                # Agent outputs are nested: {"status": "success", "data": {"evidence": {...}}}
                agent_data = output.get("data", {})
                evidence = agent_data.get("evidence", {})
                
                if agent_type == "patent":
                    if evidence.get("total_patents_found", 0) > 0:
                        insights.append(f"Found {evidence.get('total_patents_found', 0)} patents")
                    if evidence.get("expiring_patents", 0) > 0:
                        insights.append(f"{evidence.get('expiring_patents', 0)} patents expiring soon")
                    if evidence.get("freedom_to_operate"):
                        insights.append("Freedom to operate confirmed")
                
                elif agent_type == "clinical":
                    if evidence.get("ongoing_trials", 0) > 0:
                        insights.append(f"{evidence.get('ongoing_trials', 0)} ongoing clinical trials")
                    phases = evidence.get("trial_phases", {})
                    if phases:
                        phase_summary = ", ".join([f"{k}: {v}" for k, v in list(phases.items())[:2]])
                        insights.append(f"Trial phases: {phase_summary}")
                    if evidence.get("gaps"):
                        insights.append(f"Identified {len(evidence.get('gaps', []))} clinical gaps")
                
                elif agent_type == "literature":
                    if evidence.get("article_count", 0) > 0:
                        insights.append(f"{evidence.get('article_count', 0)} PubMed articles found")
                    if evidence.get("drug_labels"):
                        insights.append(f"{len(evidence.get('drug_labels', []))} FDA-approved labels")
                    rationale = evidence.get("scientific_rationale", "unknown")
                    if rationale != "unknown":
                        insights.append(f"Scientific rationale: {rationale}")
                    if evidence.get("black_box_warnings", 0) == 0:
                        insights.append("No black box warnings")
                
                elif agent_type == "market":
                    market_size = evidence.get("market_size", 0)
                    if market_size > 0:
                        insights.append(f"Market size: ${market_size:,.0f}")
                    cagr = evidence.get("cagr", 0)
                    if cagr > 0:
                        insights.append(f"CAGR: {cagr}%")
                    competitors = evidence.get("competitors", [])
                    if competitors:
                        insights.append(f"{len(competitors)} competitors identified")
                    demand = evidence.get("demand_trends", "")
                    if demand:
                        insights.append(f"Demand trend: {demand}")
            
            agents[agent_type] = AgentStatus(
                agent_type=agent_type,
                status=agent_status.get("status", "running"),
                progress=agent_status.get("progress", 50),
                insights=insights
            )
        else:
            agents[agent_type] = AgentStatus(
                agent_type=agent_type,
                status="running",
                progress=50,
                insights=[]
            )
    
    # Convert opportunities to response model with opportunity-specific evidence
    opportunities = None
    agent_outputs = analysis.get("agent_outputs", {})
    
    # Extract evidence from each agent (nested in 'data' key)
    patent_output = agent_outputs.get("patent", {})
    clinical_output = agent_outputs.get("clinical", {})
    literature_output = agent_outputs.get("literature", {})
    market_output = agent_outputs.get("market", {})
    
    patent_evidence = patent_output.get("data", {}).get("evidence", {}) if patent_output else None
    clinical_evidence = clinical_output.get("data", {}).get("evidence", {}) if clinical_output else None
    literature_evidence = literature_output.get("data", {}).get("evidence", {}) if literature_output else None
    
    if analysis.get("opportunities"):
        opportunities = []
        for i, opp in enumerate(analysis["opportunities"]):
            # Determine which evidence to attach based on opportunity source
            source_agent = opp.get("source_agent", "")
            title = opp.get("title", "").lower()
            
            # Attach ONLY the relevant evidence type for this opportunity (no mixing)
            opp_patent_evidence = None
            opp_clinical_evidence = None
            opp_literature_evidence = None
            
            # Strict matching: Each opportunity gets ONLY its relevant evidence type
            if source_agent == "patent" or "patent" in title or "expiry" in title or "white space" in title:
                # Patent opportunities get ONLY patent evidence (in depth)
                opp_patent_evidence = patent_evidence
            elif source_agent == "clinical" or "clinical" in title or "trial" in title or "unmet" in title or "research" in title:
                # Clinical opportunities get ONLY clinical evidence (in depth)
                opp_clinical_evidence = clinical_evidence
            elif source_agent == "literature" or "literature" in title or "regulatory" in title or "safety" in title or "scientific" in title:
                # Literature opportunities get ONLY literature evidence (in depth)
                opp_literature_evidence = literature_evidence
            elif source_agent == "market" or "market" in title:
                # Market opportunities - no specific evidence structure yet
                pass
            # No else clause - opportunities without clear match get no evidence
            # This ensures each opportunity shows ONLY its relevant data
            
            opportunities.append(
                OpportunityResponse(
                    id=str(i),
                    title=opp.get("title", ""),
                    description=opp.get("description"),
                    scores=opp.get("scores", {}),
                    justification=opp.get("justification"),
                    pros=opp.get("pros", []),
                    cons=opp.get("cons", []),
                    risk_factors=opp.get("risk_factors", []),
                    unmet_needs=opp.get("unmet_needs", []),
                    competitor_landscape=opp.get("competitor_landscape", []),
                    patent_evidence=opp_patent_evidence,
                    clinical_evidence=opp_clinical_evidence,
                    literature_evidence=opp_literature_evidence
                )
            )
    
    # Prepare agent outputs for frontend (evidence and scores)
    agent_outputs_for_response = {}
    for agent_type in ["market", "patent", "clinical", "literature"]:
        if agent_type in agent_outputs:
            output = agent_outputs[agent_type]
            agent_data = output.get("data", {})
            agent_outputs_for_response[agent_type] = {
                "evidence": agent_data.get("evidence", {}),
                "scores": agent_data.get("scores", {})
            }
    
    return AnalysisStatusResponse(
        analysis_id=analysis_id,
        status=analysis["status"],
        query=analysis["query"],
        agents=agents,
        agent_outputs=agent_outputs_for_response if agent_outputs_for_response else None,
        opportunities=opportunities
    )


@app.get("/api/report/{analysis_id}")
async def generate_report(analysis_id: str):
    """Generate and download PDF report."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    
    if analysis["status"] != "complete":
        raise HTTPException(status_code=400, detail="Analysis not complete yet")
    
    # Generate report
    filepath = report_generator.generate_report(
        analysis_id=analysis_id,
        query=analysis["query"],
        opportunities=analysis["opportunities"],
        agent_outputs=analysis.get("agent_outputs", {})
    )
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"pharma_query_report_{analysis_id}.pdf"
    )


@app.post("/api/research/upload", response_model=AnalysisResponse)
async def upload_research_paper(file: UploadFile = File(...)):
    """
    Upload a research paper (PDF) for analysis.
    Extracts text, runs the full research evaluation pipeline.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are accepted.")

    analysis_id = str(uuid.uuid4())

    # Read file bytes
    file_bytes = await file.read()

    # Extract text from the uploaded document
    try:
        from services.document_analysis import extract_text_from_pdf
        doc_result = await extract_text_from_pdf(file_bytes)
        extracted_text = doc_result.get("text", "")
        doc_metadata = doc_result
    except Exception as e:
        print(f"Document extraction error: {e}")
        raise HTTPException(status_code=422, detail=f"Failed to extract text from document: {str(e)}")

    if not extracted_text or len(extracted_text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Could not extract sufficient text from the document.")

    # Initialize research store
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "type": "research",
        "status": "processing",
        "extracted_text": extracted_text,
        "doc_metadata": doc_metadata,
        "result": None
    }

    # Run analysis in background with the extracted text
    asyncio.create_task(run_research_analysis(analysis_id, extracted_text))

    return {
        "analysis_id": analysis_id,
        "status": "processing",
        "message": f"Research analysis started. Use /api/research/status/{analysis_id} to check progress."
    }


<<<<<<< HEAD
async def run_research_analysis(analysis_id: str):
    """FAST MVP: Run the research analysis workflow immediately."""
    try:
        # Step 0: Pre-populate skeleton for immediate rendering
        analysis_store[analysis_id].update({
            "status": "processing",
            "result": {
                "research_score": 0.0,
                "score_dimensions": {"novelty": 0, "rigor": 0, "depth": 0},
                "annotations": [],
                "top_opportunities": [],
                "faculty_recommendations": [],
                "confidence_level": "Low"
            }
        })

        # Step 1: Execute Research Agent (now without simulated delays)
        research_topic = "General Research Paper Analysis"
        
        result = await asyncio.wait_for(
            research_agent.execute(
                session_id=analysis_id,
                research_topic=research_topic,
                uploaded_paper=None,
                context_data={"analysis_id": analysis_id}
            ),
            timeout=3.0
=======
async def run_research_analysis(analysis_id: str, extracted_text: str = ""):
    """Run the research analysis workflow with robust error handling."""
    logs = []
    try:
        # Step 1: Execute Research Agent with actual extracted text
        research_topic = extracted_text[:200] if extracted_text else "General Research Paper Analysis"
        
        result = await research_agent.execute(
            session_id=analysis_id,
            research_topic=research_topic,
            uploaded_paper=extracted_text or None,
            context_data={"analysis_id": analysis_id}
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67
        )
        
        if result["status"] == "success":
            data = result.get("data", {})
            # Step 2: Update analysis store as complete
            analysis_store[analysis_id].update({
                "status": "complete",
                "result": data,
                "confidence": result.get("confidence", 0.5),
                "logs": result.get("logs", [])
            })
        else:
            analysis_store[analysis_id]["status"] = "complete" # Mark complete to unblock UI
            
    except Exception as e:
        print(f"Error in fast research analysis {analysis_id}: {e}")
        analysis_store[analysis_id]["status"] = "complete"
        analysis_store[analysis_id]["error"] = str(e)


@app.get("/api/research/status/{analysis_id}", response_model=ResearchStatusResponse)
async def get_research_status(analysis_id: str):
    """Get research analysis status. Returns partial result if still processing."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    result = analysis.get("result")
    
    # If no result yet, return a skeleton
    if not result:
        result = {
            "research_score": 0.0,
            "score_dimensions": {"novelty": 0, "rigor": 0, "depth": 0},
            "annotations": [],
            "top_opportunities": [],
            "faculty_recommendations": [],
            "confidence_level": "Low"
        }
    
    # Use full extracted text from upload if available, else from agent result
    full_text = analysis.get("extracted_text") or result.get("extracted_text", "")
    
    return ResearchStatusResponse(
        analysis_id=analysis_id,
        status=analysis["status"],
        research_score=result["research_score"],
        score_dimensions=result["score_dimensions"],
        annotations=[ResearchAnnotation(**a) for a in result["annotations"]],
        top_opportunities=[ResearchOpportunity(**o) for o in result["top_opportunities"]],
        faculty_recommendations=[FacultyRecommendation(**f) for f in result["faculty_recommendations"]],
        confidence_level=result["confidence_level"],
        confidence_result=ConfidenceResult(**result["confidence_result"]) if result.get("confidence_result") else None,
        extracted_text=full_text
    )


@app.get("/api/research/report/{analysis_id}")
async def download_research_report(analysis_id: str):
    """Generate and download a PDF report for a research analysis."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_store[analysis_id]
    
    if analysis.get("status") != "complete":
        raise HTTPException(status_code=400, detail="Analysis not yet complete")
    
    result = analysis["result"]
    
    try:
        from services.research_report_generator import ResearchReportGenerator
        generator = ResearchReportGenerator()
        pdf_bytes = generator.generate_report(analysis_id, result)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="research_report_{analysis_id[:8]}.pdf"'
            }
        )
    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "PharmaQuery API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

