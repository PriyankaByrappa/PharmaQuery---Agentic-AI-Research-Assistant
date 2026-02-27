"""Scoring Engine - combines agent outputs into composite scores."""
from typing import Dict, Any, List
from config import SCORING_WEIGHTS


class ScoringEngine:
    """Engine that calculates composite scores for opportunities."""
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or SCORING_WEIGHTS
    
    def score_opportunities(self, agent_outputs: Dict[str, Dict[str, Any]], 
                          aggregated_opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        FAST MVP: Basic score aggregation.
        """
        scored_opportunities = []
        
        for opp in aggregated_opportunities:
            market_score = self._get_agent_score(agent_outputs, "market", opp)
            patent_score = self._get_agent_score(agent_outputs, "patent", opp)
            clinical_score = self._get_agent_score(agent_outputs, "clinical", opp)
            literature_score = self._get_agent_score(agent_outputs, "literature", opp)
            
            # Simple average
            composite_score = (market_score + patent_score + clinical_score + literature_score) / 4.0
            
            scored_opp = {
                **opp,
                "scores": {
                    "market": market_score,
                    "patent": patent_score,
                    "clinical": clinical_score,
                    "literature": literature_score,
                    "composite": round(composite_score, 2)
                },
                "justification": "Primary opportunity identified by automated screening.",
                "pros": ["Strong scientific basis", "Market potential"],
                "cons": ["Standard regulatory risks"],
                "risk_factors": ["Regulatory approval timeline", "Market competition"],
                "unmet_needs": ["Improved efficacy", "Better safety profile"],
                "competitor_landscape": ["Standard market competitors"]
            }
            
            scored_opportunities.append(scored_opp)
        
        scored_opportunities.sort(key=lambda x: x["scores"]["composite"], reverse=True)
        return scored_opportunities
    
    def _get_agent_score(self, agent_outputs: Dict[str, Dict[str, Any]], 
                        agent_type: str, opportunity: Dict[str, Any]) -> float:
        """Get relevant score from agent output for this opportunity."""
        if agent_type not in agent_outputs:
            return 0.0
        
        agent_result = agent_outputs[agent_type]
        if agent_result.get("status") != "success":
            return 0.0
            
        agent_data = agent_result.get("data", {})
        scores = agent_data.get("scores", {})
        
        # Try to match opportunity to agent's opportunities
        agent_opportunities = agent_data.get("top_opportunities", [])
        source_agent = opportunity.get("source_agent", "")
        
        if source_agent == agent_type:
            # Use the primary score for this agent
            if agent_type == "market":
                return scores.get("market_potential", 0.0)
            elif agent_type == "patent":
                return scores.get("patent_score", 0.0)
            elif agent_type == "clinical":
                return scores.get("clinical_score", 0.0)
            elif agent_type == "literature":
                return scores.get("literature_score", 0.0)
        
        # Default: use average of all scores from this agent
        if scores:
            valid_scores = [v for v in scores.values() if isinstance(v, (int, float))]
            if valid_scores:
                return sum(valid_scores) / len(valid_scores)
        
        return 0.5  # Default neutral score
    
    def _generate_justification(self, opportunity: Dict[str, Any], 
                               market: float, patent: float, clinical: float, 
                               literature: float) -> str:
        """Generate justification text for the opportunity."""
        justifications = []
        
        if market > 0.7:
            justifications.append("Strong commercial viability with high market potential")
        if patent > 0.7:
            justifications.append("Favorable patent landscape with freedom to operate")
        if clinical > 0.7:
            justifications.append("Active clinical research and identified gaps")
        if literature > 0.7:
            justifications.append("Strong scientific rationale and regulatory foundation")
        
        if not justifications:
            return "Moderate opportunity with balanced scores across all dimensions"
        
        return ". ".join(justifications) + "."
    
    def _generate_pros(self, opportunity: Dict[str, Any], 
                      agent_outputs: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate pros for the opportunity."""
        pros = []
        
        # Helper to get safe data
        def get_data(atype):
            res = agent_outputs.get(atype, {})
            return res.get("data", {}) if res.get("status") == "success" else {}

        # Market pros
        market_data = get_data("market")
        if market_data.get("evidence", {}).get("cagr", 0) > 5:
            pros.append(f"High growth potential ({market_data['evidence']['cagr']}% CAGR)")
        
        # Patent pros
        patent_data = get_data("patent")
        if patent_data.get("evidence", {}).get("freedom_to_operate"):
            pros.append("Freedom to operate confirmed")
        
        # Clinical pros
        clinical_data = get_data("clinical")
        if clinical_data.get("evidence", {}).get("ongoing_trials", 0) > 0:
            pros.append("Active clinical research ongoing")
        
        # Literature pros
        literature_data = get_data("literature")
        if literature_data.get("evidence", {}).get("black_box_warnings", 0) == 0:
            pros.append("Favorable safety profile")
        
        return pros if pros else ["Balanced opportunity across multiple dimensions"]
    
    def _generate_cons(self, opportunity: Dict[str, Any], 
                      agent_outputs: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate cons for the opportunity."""
        cons = []
        
        # Helper to get safe data
        def get_data(atype):
            res = agent_outputs.get(atype, {})
            return res.get("data", {}) if res.get("status") == "success" else {}

        # Market cons
        market_data = get_data("market")
        competitors = len(market_data.get("evidence", {}).get("competitors", []))
        if competitors > 5:
            cons.append(f"High competition ({competitors} major competitors)")
        
        # Patent cons
        patent_data = get_data("patent")
        if not patent_data.get("evidence", {}).get("freedom_to_operate"):
            cons.append("Potential IP barriers")
        
        # Clinical cons
        clinical_data = get_data("clinical")
        if clinical_data.get("evidence", {}).get("trial_failures", 0) > 2:
            cons.append("Some clinical trial failures observed")
        
        # Literature cons
        literature_data = get_data("literature")
        if literature_data.get("evidence", {}).get("black_box_warnings", 0) > 0:
            cons.append("Black box warnings present")
        
        return cons if cons else ["Standard risks associated with drug repurposing"]
    
    def _identify_risks(self, opportunity: Dict[str, Any], 
                       agent_outputs: Dict[str, Dict[str, Any]],
                       source_agent: str = "") -> List[str]:
        """Identify risk factors - opportunity-specific based on source agent."""
        risks = []
        title = opportunity.get("title", "").lower()
        
        # Helper to get safe data
        def get_data(atype):
            res = agent_outputs.get(atype, {})
            return res.get("data", {}) if res.get("status") == "success" else {}

        # Patent-specific risks
        if source_agent == "patent" or "patent" in title:
            patent_data = get_data("patent")
            patent_evidence = patent_data.get("evidence", {})
            
            if not patent_evidence.get("freedom_to_operate", True):
                risks.append("Potential IP barriers and patent infringement risks")
            
            active_patents = patent_evidence.get("active_patents", 0)
            if active_patents > 10:
                risks.append("High patent density may limit freedom to operate")
            
            expiring = patent_evidence.get("expiring_patents", 0)
            if expiring == 0 and active_patents > 0:
                risks.append("No near-term patent expiry opportunities")
            
            density = patent_evidence.get("patent_density", "")
            if density == "high":
                risks.append("Crowded IP landscape with high patent density")
            
            if not risks:  # If no specific patent risks, add generic IP risk
                risks.append("Standard IP and patent landscape risks")
        
        # Clinical-specific risks
        elif source_agent == "clinical" or "clinical" in title or "trial" in title:
            clinical_data = get_data("clinical")
            clinical_evidence = clinical_data.get("evidence", {})
            
            failures = clinical_evidence.get("trial_failures", 0)
            if failures > 2:
                risks.append("Multiple clinical trial failures observed")
            
            gaps = clinical_evidence.get("gaps", [])
            if len(gaps) > 3:
                risks.append("Multiple clinical evidence gaps requiring additional studies")
            
            ongoing = clinical_evidence.get("ongoing_trials", 0)
            if ongoing == 0:
                risks.append("No active clinical research currently ongoing")
            
            phases = clinical_evidence.get("trial_phases", {})
            if phases and "Phase III" not in str(phases) and "Phase IV" not in str(phases):
                risks.append("Limited late-stage clinical evidence")
            
            if not risks:  # If no specific clinical risks, add generic trial risk
                risks.append("Standard clinical trial and regulatory risks")
        
        # Literature-specific risks
        elif source_agent == "literature" or "literature" in title or "regulatory" in title:
            literature_data = get_data("literature")
            literature_evidence = literature_data.get("evidence", {})
            
            if literature_evidence.get("black_box_warnings", 0) > 0:
                risks.append("Black box warnings present - significant safety concerns")
            
            article_count = literature_evidence.get("article_count", 0)
            if article_count < 5:
                risks.append("Limited scientific literature support")
            
            rationale = literature_evidence.get("scientific_rationale", "unknown")
            if rationale == "Low" or rationale == "unknown":
                risks.append("Weak scientific rationale for repurposing")
            
            if not risks:  # If no specific literature risks, add generic regulatory risk
                risks.append("Standard regulatory and safety risks")
        
        # Market-specific risks (when implemented)
        elif source_agent == "market" or "market" in title:
            market_data = get_data("market")
            market_evidence = market_data.get("evidence", {})
            
            if market_evidence.get("cagr", 0) < 3:
                risks.append("Low market growth rate")
            
            competitors = market_evidence.get("competitors", [])
            if len(competitors) > 5:
                risks.append("High competition in target market")
        
        # Common risks (if no specific risks identified for this opportunity type)
        if not risks:
            # Add general risks that apply to all opportunities
            risks.append("Standard regulatory and market risks")
            risks.append("Drug repurposing requires regulatory approval")
        
        return risks
    
    def _extract_unmet_needs(self, opportunity: Dict[str, Any], 
                            agent_outputs: Dict[str, Dict[str, Any]],
                            source_agent: str = "") -> List[str]:
        """Extract unmet needs - opportunity-specific based on source agent."""
        unmet_needs = []
        title = opportunity.get("title", "").lower()
        
        # Helper to get safe data
        def get_data(atype):
            res = agent_outputs.get(atype, {})
            return res.get("data", {}) if res.get("status") == "success" else {}

        # Patent-specific unmet needs
        if source_agent == "patent" or "patent" in title:
            patent_data = get_data("patent")
            patent_evidence = patent_data.get("evidence", {})
            
            white_space = patent_evidence.get("white_space", [])
            if white_space:
                unmet_needs.extend(white_space[:3])  # Top 3 white space areas
            
            if patent_evidence.get("freedom_to_operate") and patent_evidence.get("active_patents", 0) == 0:
                unmet_needs.append("Novel patent opportunities in unpatented space")
            
            if patent_evidence.get("patent_density") == "low":
                unmet_needs.append("Low patent density - opportunity for new IP development")
        
        # Clinical-specific unmet needs
        elif source_agent == "clinical" or "clinical" in title or "trial" in title:
            clinical_data = get_data("clinical")
            clinical_evidence = clinical_data.get("evidence", {})
            
            # Use clinical agent's unmet needs
            clinical_unmet = clinical_evidence.get("unmet_needs", [])
            if clinical_unmet:
                unmet_needs.extend(clinical_unmet)
            
            # Add gaps as unmet needs
            gaps = clinical_evidence.get("gaps", [])
            if gaps:
                unmet_needs.extend(gaps[:3])  # Top 3 gaps
            
            # If no specific unmet needs, add generic ones
            if not unmet_needs:
                if clinical_evidence.get("ongoing_trials", 0) < 3:
                    unmet_needs.append("Limited active research")
                if "Phase III" not in str(clinical_evidence.get("trial_phases", {})):
                    unmet_needs.append("Need for Phase III evidence")
        
        # Literature-specific unmet needs
        elif source_agent == "literature" or "literature" in title or "regulatory" in title:
            literature_data = get_data("literature")
            literature_evidence = literature_data.get("evidence", {})
            
            if literature_evidence.get("article_count", 0) < 10:
                unmet_needs.append("Need for more scientific evidence")
            
            rationale = literature_evidence.get("scientific_rationale", "unknown")
            if rationale == "Low":
                unmet_needs.append("Need for stronger scientific rationale")
            
            if literature_evidence.get("drug_labels", []):
                unmet_needs.append("Regulatory pathway exists - opportunity for label expansion")
            else:
                unmet_needs.append("Need for regulatory approval in target indication")
        
        # Market-specific unmet needs (when implemented)
        elif source_agent == "market" or "market" in title:
            market_data = get_data("market")
            market_evidence = market_data.get("evidence", {})
            
            if market_evidence.get("cagr", 0) < 5:
                unmet_needs.append("Need for market growth acceleration")
            
            competitors = market_evidence.get("competitors", [])
            if len(competitors) < 3:
                unmet_needs.append("Opportunity in less competitive market segment")
        
        # Fallback to clinical unmet needs if no specific needs found
        if not unmet_needs:
            clinical_data = get_data("clinical")
            clinical_unmet = clinical_data.get("evidence", {}).get("unmet_needs", [])
            if clinical_unmet:
                unmet_needs.extend(clinical_unmet[:2])  # Top 2 as fallback
        
        return unmet_needs[:5]  # Limit to top 5
    
    def _extract_competitors(self, opportunity: Dict[str, Any], 
                           agent_outputs: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract competitor landscape."""
        res = agent_outputs.get("market", {})
        market_data = res.get("data", {}) if res.get("status") == "success" else {}
        return market_data.get("evidence", {}).get("competitors", [])

