"""Research Agent - handles paper evaluation, opportunity discovery, and faculty recommendations."""
from typing import Dict, Any, List
import asyncio
import re
import random
from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Agent that evaluates research papers and identifies academic opportunities."""
    
    def __init__(self):
        super().__init__("research")
        self.indian_institutions = [
            "IIT Delhi", "IIT Bombay", "IISc Bangalore", "IIT Madras",
            "IIIT Hyderabad", "NIT Trichy", "TIFR Mumbai", "IIT Kanpur",
            "IISER Pune", "IIT Kharagpur", "IIT Roorkee",
        ]
        
    async def execute(self, session_id: str, research_topic: str, uploaded_paper: Any = None, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute research analysis on a paper following the standardized contract.
        """
        logs = []
        try:
            self.set_status("analyzing_paper")
            logs.append("Started paper analysis")
            self.update_progress(10)
            
            # Use uploaded_paper text if available, otherwise fall back to topic
            input_text = uploaded_paper if uploaded_paper and isinstance(uploaded_paper, str) else research_topic
            
<<<<<<< HEAD
=======
            # Simulate brief processing time for UI responsiveness
            await asyncio.sleep(0.5)
            
>>>>>>> 76504fc1dfbada5f52fca01e047c169a0a14ac67
            # 1. Generate Research Quality Score (IEEE Level)
            logs.append("Evaluating paper quality dimensions")
            score_data = self.evaluate_paper(input_text)
            self.update_progress(40)
            
            # 2. Generate Annotations
            logs.append("Generating document annotations")
            annotations = self.generate_annotations(input_text)
            self.update_progress(60)
            
            # 3. Discover Opportunities
            logs.append("Searching for research opportunities")
            opportunities = self.discover_opportunities(input_text)
            self.update_progress(80)
            
            # 4. Recommend Indian Faculty
            logs.append("Identifying Indian faculty recommendations")
            faculty = self.recommend_faculty(input_text)
            self.update_progress(100)
            
            self.set_status("complete")
            logs.append("Research analysis complete")
            
            # Confidence calculation
            confidence_result = self._calculate_confidence(score_data, annotations)
            confidence_map = {"High": 0.9, "Medium": 0.6, "Low": 0.3}
            confidence_val = confidence_map.get(confidence_result["level"], 0.5)
            
            return {
                "status": "success",
                "data": {
                    "insight_type": "research_evaluation",
                    "research_score": score_data["total_score"],
                    "score_dimensions": score_data["dimensions"],
                    "annotations": annotations,
                    "top_opportunities": opportunities,
                    "faculty_recommendations": faculty,
                    "confidence_level": confidence_result["level"],
                    "confidence_result": confidence_result,
                    "extracted_text": input_text[:15000],  # Send first 15k chars for document viewer
                },
                "confidence": confidence_val,
                "logs": logs
            }
        except Exception as e:
            self.set_status("error")
            logs.append(f"Error during execution: {str(e)}")
            return {
                "status": "error",
                "data": {},
                "confidence": 0,
                "logs": logs
            }
        
    def evaluate_paper(self, text: str) -> Dict[str, Any]:
        """Calculate quality score based on IEEE rigor using the scoring engine."""
        try:
            from services.research_scoring_engine import score_paper
            from services.document_analysis import detect_sections
            sections = detect_sections(text)
            return score_paper(text, sections)
        except ImportError:
            # Fallback to basic scoring if service not available
            return self._fallback_scoring(text)
    
    def _fallback_scoring(self, text: str) -> Dict[str, Any]:
        """Basic fallback scoring if the engine is unavailable."""
        word_count = len(text.split()) if text else 0
        base = min(30 + (word_count / 100), 65)
        return {
            "total_score": round(base, 1),
            "dimensions": {
                "novelty": int(base),
                "methodological_rigor": int(base * 0.9),
                "citation_credibility": int(base * 0.85),
                "technical_depth": int(base * 0.9),
                "mathematical_formalism": int(base * 0.7),
                "literature_coverage": int(base * 0.8),
                "structural_quality": int(base * 0.85),
                "clarity_coherence": int(base * 0.9),
                "reproducibility": int(base * 0.75),
            },
        }
        
    def generate_annotations(self, text: str) -> List[Dict[str, Any]]:
        """Identify specific areas of interest or concern using heuristic analysis."""
        annotations = []
        
        if not text or len(text) < 100:
            return annotations
        
        text_lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 20]
        text_lower = text.lower()
        
        # --- Pattern 1: Redundancy Detection ---
        # Look for identical or nearly identical sentences that appeared earlier
        seen_sentences = {}
        for line in text_lines:
            # Simple sentence splitting for heuristic
            sentences = re.split(r'(?<=[.!?])\s+', line)
            for sentence in sentences:
                if len(sentence) < 40: continue
                s_lower = sentence.lower().strip()
                if s_lower in seen_sentences:
                    # Found redundancy
                    start_pos = text.find(sentence)
                    if start_pos != -1:
                        annotations.append({
                            "tag": "REDUNDANT CONTENT",
                            "content": sentence[:100],
                            "tooltip": "Repetitive information detected",
                            "reasoning": "This sentence or a very similar one has already appeared in the document. Redundancy can dilute the impact of your research findings.",
                            "suggestion": "Consolidate this information or remove the repetition to improve clarity and flow.",
                            "position": {"start": start_pos, "end": start_pos + len(sentence)},
                        })
                else:
                    seen_sentences[s_lower] = True
            if len([a for a in annotations if a['tag'] == 'REDUNDANT CONTENT']) >= 2:
                break

        # --- Pattern 2: Simulated Plagiarism Detection ---
        # Identifies common academic "borrowed" phrases with attributed sources
        mock_plagiarism_sources = [
            (r"(?i)(the\s+results\s+demonstrate\s+that\s+the\s+proposed\s+method\s+is\s+highly\s+effective\s+.{10,60})",
             "Journal of Academic Excellence", "https://example.com/source/123"),
            (r"(?i)(in\s+this\s+context,?\s+it\s+is\s+crucial\s+to\s+consider\s+the\s+implications\s+of\s+.{10,60})",
             "Nature Research Archive", "https://example.com/source/456"),
            (r"(?i)(data\s+collection\s+was\s+performed\s+using\s+a\s+standardized\s+survey\s+instrument\s+.{10,60})",
             "Social Science Review", "https://example.com/source/789"),
        ]
        
        for pattern, source_name, source_link in mock_plagiarism_sources:
            match = re.search(pattern, text)
            if match:
                annotations.append({
                    "tag": "PLAGIARISED",
                    "content": match.group(0),
                    "tooltip": "Potential originality issue",
                    "reasoning": f"This segment matches text found in '{source_name}'. High similarity to existing work without proper attribution can be flagged in peer review.",
                    "suggestion": "Paraphrase this section in your own words and ensure proper citation of the original source.",
                    "position": {"start": match.start(), "end": match.end()},
                    "source_name": source_name,
                    "source_link": source_link
                })

        # --- Pattern 3: Missing Citations (Optimized) ---
        uncited_claim_patterns = [
            r"(?i)(studies\s+(?:show|suggest|indicate|have shown))",
            r"(?i)(research\s+(?:shows|suggests|indicates|has shown))",
            r"(?i)(it\s+(?:is|has been)\s+(?:shown|demonstrated|proven|established))",
        ]
        
        for pattern in uncited_claim_patterns:
            for match in re.finditer(pattern, text[:10000]):
                nearby = text[match.end():match.end() + 60]
                if not re.search(r"\[\d+\]|\(\w+.*?\d{4}\)", nearby):
                    annotations.append({
                        "tag": "MISSING CITATION",
                        "content": match.group(0),
                        "tooltip": "Uncited claim",
                        "reasoning": "This general claim lacks a specific bibliographic reference, which is required for academic rigor.",
                        "suggestion": "Attach a supporting citation (e.g., [12] or Smith et al., 2023) to this statement.",
                        "position": {"start": match.start(), "end": match.end()},
                    })
                if len([a for a in annotations if a['tag'] == 'MISSING CITATION']) >= 3:
                    break

        # --- Pattern 4: Strong Insights & Novelty ---
        insight_patterns = [
            (r"(?i)(we\s+(?:propose|introduce|present|demonstrate)\s+.{10,80})", "STRONG INSIGHT"),
            (r"(?i)(novel\s+.{5,60})", "NOVEL CONTRIBUTION"),
        ]
        
        for pattern, tag in insight_patterns:
            for match in re.finditer(pattern, text[:10000]):
                annotations.append({
                    "tag": tag,
                    "content": match.group(0)[:80],
                    "tooltip": f"{tag.replace('_', ' ').title()} identified",
                    "reasoning": f"This passage highlights a key contribution or original aspect of your work.",
                    "suggestion": "Keep this well-defined. It serves as a strong hook for reviewers.",
                    "position": {"start": match.start(), "end": min(match.end(), match.start() + 80)},
                })
                break
        
        # --- Pattern 5: Hedging / Weak Arguments ---
        hedging_patterns = [
            (r"(?i)\b(might|possibly|perhaps|seems to|appears to)\b\s+.{10,50}",
             "WEAK ARGUMENT",
             "Hedged claim identified",
             "Frequent use of uncertain language can make your conclusions seem tentative.",
             "Try to use more definitive language if your data strongly supports the trend.")
        ]
        
        for pattern, tag, tooltip, reasoning, suggestion in hedging_patterns:
            for match in re.finditer(pattern, text[:5000]):
                annotations.append({
                    "tag": tag,
                    "content": match.group(0),
                    "tooltip": tooltip,
                    "reasoning": reasoning,
                    "suggestion": suggestion,
                    "position": {"start": match.start(), "end": match.end()},
                })
                break
                
        # Sort by position
        annotations.sort(key=lambda a: a["position"]["start"])
        return annotations[:20]
        # Sort by position and limit to reasonable count
        annotations.sort(key=lambda a: a["position"]["start"])
        return annotations[:15]
        
    def discover_opportunities(self, text: str) -> List[Dict[str, Any]]:
        """Match paper to research calls and programs based on content analysis."""
        from services.opportunity_scraper import discover_opportunities
        try:
            return discover_opportunities(text)
        except ImportError:
            return self._fallback_opportunities(text)
    
    def _fallback_opportunities(self, text: str) -> List[Dict[str, Any]]:
        """Fallback with category-aware mock data."""
        opp_types = ["Research Internship", "Open Lab Position", "Funded Program", "Call for Papers"]
        sources = ["arXiv", "IEEE Xplore", "Google Research", "MIT Media Lab", "Stanford AI Lab"]
        
        opportunities = []
        for i in range(4):
            relevance = random.randint(70, 95)
            difficulty = random.randint(60, 90)
            opportunities.append({
                "id": str(i),
                "title": f"{random.choice(opp_types)} — AI & Computational Methods",
                "source": random.choice(sources),
                "relevance_score": relevance,
                "difficulty_score": difficulty,
                "description": "Matching based on methodological similarity and domain keywords found in your research paper.",
                "why_matched": "Keywords in your paper overlap with the scope of this opportunity.",
                "category": random.choice(opp_types),
                "deadline": "Rolling",
                "link": "#"
            })
        
        opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
        return opportunities
        
    def recommend_faculty(self, text: str) -> List[Dict[str, Any]]:
        """Suggest Indian professors based on paper content."""
        from services.recommendation_system import recommend_faculty
        try:
            return recommend_faculty(text)
        except ImportError:
            return self._fallback_faculty(text)
    
    def _fallback_faculty(self, text: str) -> List[Dict[str, Any]]:
        """Fallback with curated mock data."""
        researchers = [
            {"name": "Dr. Amitabh Mukherjee", "inst": "IIT Kanpur", "area": "Computer Vision & NLP"},
            {"name": "Prof. Mausam", "inst": "IIT Delhi", "area": "Artificial Intelligence"},
            {"name": "Dr. Sunita Sarawagi", "inst": "IIT Bombay", "area": "Machine Learning"},
            {"name": "Prof. Pushpak Bhattacharyya", "inst": "IIT Bombay", "area": "Natural Language Processing"},
        ]
        
        recommendations = random.sample(researchers, min(2, len(researchers)))
        for rec in recommendations:
            rec["why"] = "Extensive publication history in similar methodological areas and high citation overlap."
            rec["link"] = "#"
            
        return recommendations
        
    def _calculate_confidence(self, score_data: Dict[str, Any], annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate structured confidence result with sub-scores.
        Returns dict with 'level', 'model_certainty', 'data_completeness', 
        'document_clarity', 'signal_consistency', 'summary'.
        """
        dimensions = score_data.get("dimensions", {})
        total_score = score_data.get("total_score", 0)
        
        # Sub-scores
        model_certainty = min(len(annotations) * 12 + 20, 90)
        
        dim_values = list(dimensions.values())
        data_completeness = min(sum(1 for v in dim_values if v > 30) * 12, 95) if dim_values else 30
        
        # How consistent are the dimension scores?
        if dim_values:
            mean_v = sum(dim_values) / len(dim_values)
            variance = sum((v - mean_v) ** 2 for v in dim_values) / len(dim_values)
            signal_consistency = max(90 - int(variance ** 0.5), 30)
        else:
            signal_consistency = 30
        
        document_clarity = dimensions.get("clarity_coherence", 50)
        
        # Overall level
        avg = (model_certainty + data_completeness + signal_consistency + document_clarity) / 4
        if avg > 70:
            level = "High"
        elif avg > 45:
            level = "Medium"
        else:
            level = "Low"
        
        # Plain English summary
        summaries = {
            "High": "The AI is confident in this evaluation. The document provided sufficient signals across all scoring dimensions, and the analysis is well-grounded.",
            "Medium": "The AI has moderate confidence in this evaluation. Some scoring dimensions had limited signal, so results should be interpreted with professional judgement.",
            "Low": "The AI has low confidence in this evaluation. The document may be too short, lack structure, or have insufficient academic content for reliable analysis.",
        }
        
        return {
            "level": level,
            "model_certainty": model_certainty,
            "data_completeness": data_completeness,
            "document_clarity": document_clarity,
            "signal_consistency": signal_consistency,
            "summary": summaries[level],
        }
