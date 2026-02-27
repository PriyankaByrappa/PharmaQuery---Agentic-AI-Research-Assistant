"""Opportunity Discovery Service — Keyword-matched research opportunity finder.

Matches paper content against a curated database of research opportunity types.
Uses keyword overlap and domain matching for relevance scoring.
"""
import re
import random
from typing import Dict, Any, List


# ─── Curated opportunity database ──────────────────────────────────────────────
OPPORTUNITY_TEMPLATES = [
    {
        "title": "SERB Core Research Grant — {domain}",
        "source": "SERB India",
        "category": "Funded Program",
        "base_link": "https://serb.gov.in/page/english/awards_fellowship",
        "keywords": ["machine learning", "deep learning", "optimization", "algorithm", "framework"],
        "deadline": "Rolling (quarterly cycles)",
    },
    {
        "title": "IEEE International Conference on {domain}",
        "source": "IEEE Xplore",
        "category": "Call for Papers",
        "base_link": "https://www.ieee.org/conferences/index.html",
        "keywords": ["neural network", "transformer", "attention", "computer vision", "nlp", "artificial intelligence"],
        "deadline": "Varies — check CFP",
    },
    {
        "title": "Google Research Scholar Program — {domain}",
        "source": "Google Research",
        "category": "Research Internship",
        "base_link": "https://research.google/outreach/research-scholar-program/",
        "keywords": ["research", "machine learning", "ai", "deep learning", "language model"],
        "deadline": "April annually",
    },
    {
        "title": "ACM Computing Surveys — Special Issue on {domain}",
        "source": "ACM Digital Library",
        "category": "Call for Papers",
        "base_link": "https://dl.acm.org/journal/csur",
        "keywords": ["survey", "review", "analysis", "benchmark", "evaluation", "comparison"],
        "deadline": "Open submission",
    },
    {
        "title": "DST INSPIRE Faculty Fellowship — {domain}",
        "source": "DST India",
        "category": "Funded Program",
        "base_link": "https://www.online-inspire.gov.in/",
        "keywords": ["research", "science", "engineering", "innovation", "pharmaceutical", "biomedical"],
        "deadline": "September annually",
    },
    {
        "title": "MITACS Globalink Research Internship — {domain}",
        "source": "MITACS Canada",
        "category": "Research Internship",
        "base_link": "https://www.mitacs.ca/en/programs/globalink",
        "keywords": ["research", "computational", "data science", "algorithm", "optimization"],
        "deadline": "September annually",
    },
    {
        "title": "Springer Nature — Research Position in {domain}",
        "source": "Nature Research",
        "category": "Open Lab Position",
        "base_link": "https://www.nature.com/naturecareers",
        "keywords": ["drug discovery", "pharmaceutical", "clinical", "biomedical", "protein", "molecular"],
        "deadline": "Rolling",
    },
    {
        "title": "arXiv Spotlight — Trending in {domain}",
        "source": "arXiv",
        "category": "Call for Papers",
        "base_link": "https://arxiv.org/",
        "keywords": ["novel", "state-of-the-art", "breakthrough", "approach", "model", "architecture"],
        "deadline": "Open submission",
    },
]

# Domain keywords for contextual matching
DOMAIN_KEYWORDS = {
    "Artificial Intelligence": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
    "Natural Language Processing": ["nlp", "language model", "text", "sentiment", "translation", "bert", "gpt", "transformer"],
    "Computer Vision": ["vision", "image", "object detection", "segmentation", "cnn", "convolution"],
    "Drug Discovery": ["drug", "pharmaceutical", "molecule", "protein", "binding", "clinical", "compound"],
    "Bioinformatics": ["gene", "dna", "rna", "protein", "sequence", "genome", "bioinformatics"],
    "Data Science": ["data", "analytics", "statistics", "visualization", "clustering", "classification"],
    "Robotics": ["robot", "autonomous", "navigation", "control", "sensor", "actuator"],
    "Computational Methods": ["algorithm", "optimization", "complexity", "computation", "simulation"],
}


def discover_opportunities(text: str) -> List[Dict[str, Any]]:
    """
    Match paper content to research opportunities.
    
    Args:
        text: Full extracted text of the paper.
    
    Returns:
        List of opportunity dicts sorted by relevance.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    
    # Detect primary domain
    domain = _detect_domain(text_lower)
    
    # Extract key phrases for matching
    paper_keywords = _extract_keywords(text_lower)
    
    opportunities = []
    
    for i, template in enumerate(OPPORTUNITY_TEMPLATES):
        # Calculate keyword overlap
        overlap = sum(1 for kw in template["keywords"] if kw in text_lower)
        if overlap == 0:
            continue
        
        # Relevance score: keyword overlap * 15, capped at 95
        relevance = min(50 + overlap * 12, 95)
        
        # Difficulty: varies by category
        difficulty_map = {
            "Funded Program": random.randint(70, 88),
            "Call for Papers": random.randint(55, 75),
            "Research Internship": random.randint(60, 80),
            "Open Lab Position": random.randint(65, 85),
        }
        difficulty = difficulty_map.get(template["category"], 70)
        
        # Build why_matched explanation
        matched_keywords = [kw for kw in template["keywords"] if kw in text_lower]
        why = f"Your paper mentions {', '.join(matched_keywords[:3])}, which aligns with the scope of this opportunity."
        
        opportunities.append({
            "id": str(i),
            "title": template["title"].replace("{domain}", domain),
            "source": template["source"],
            "relevance_score": relevance,
            "difficulty_score": difficulty,
            "description": f"Opportunity matched based on {len(matched_keywords)} keyword overlaps with your research content.",
            "why_matched": why,
            "category": template["category"],
            "deadline": template["deadline"],
            "link": template["base_link"],
        })
    
    # Sort by relevance descending
    opportunities.sort(key=lambda x: x["relevance_score"], reverse=True)
    return opportunities[:6]  # Top 6


def _detect_domain(text: str) -> str:
    """Detect the primary domain of the paper."""
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[domain] = score
    
    if not scores or max(scores.values()) == 0:
        return "Computational Research"
    
    return max(scores, key=scores.get)


def _extract_keywords(text: str) -> List[str]:
    """Extract significant keywords from the text."""
    # Simple approach: find technical-sounding words
    words = re.findall(r'\b[a-z]{4,}\b', text)
    word_freq = {}
    stop_words = {"this", "that", "with", "from", "have", "been", "were", "they", "their", "which", "would", "could", "should",
                  "about", "these", "those", "than", "into", "also", "more", "most", "some", "such", "each", "other"}
    
    for w in words:
        if w not in stop_words:
            word_freq[w] = word_freq.get(w, 0) + 1
    
    # Return top keywords by frequency
    sorted_kw = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [kw for kw, _ in sorted_kw[:20]]
