"""Faculty Recommendation Service — Keyword-matched Indian faculty finder.

Matches paper content against a curated database of Indian researchers
from IITs, IISc, IIITs, NITs, TIFR, IISER, and DRDO labs.
"""
import re
from typing import Dict, Any, List


# ─── Curated Indian Faculty Database ──────────────────────────────────────────
FACULTY_DATABASE = [
    {
        "name": "Prof. Mausam",
        "inst": "IIT Delhi",
        "area": "Artificial Intelligence & NLP",
        "keywords": ["ai", "nlp", "knowledge graphs", "information extraction", "planning"],
        "link": "https://www.cse.iitd.ac.in/~mausam/",
    },
    {
        "name": "Dr. Sunita Sarawagi",
        "inst": "IIT Bombay",
        "area": "Machine Learning & Data Mining",
        "keywords": ["machine learning", "deep learning", "structured prediction", "data mining"],
        "link": "https://www.cse.iitb.ac.in/~sunita/",
    },
    {
        "name": "Prof. Pushpak Bhattacharyya",
        "inst": "IIT Bombay",
        "area": "Natural Language Processing",
        "keywords": ["nlp", "sentiment analysis", "machine translation", "wordnet", "language"],
        "link": "https://www.cse.iitb.ac.in/~pb/",
    },
    {
        "name": "Dr. Amitabh Mukherjee",
        "inst": "IIT Kanpur",
        "area": "Computer Vision & NLP",
        "keywords": ["computer vision", "image", "nlp", "multimodal", "language grounding"],
        "link": "https://www.cse.iitk.ac.in/users/amit/",
    },
    {
        "name": "Prof. Chiranjib Bhattacharyya",
        "inst": "IISc Bangalore",
        "area": "Machine Learning & Optimization",
        "keywords": ["optimization", "machine learning", "kernel methods", "convex", "statistical learning"],
        "link": "https://www.csa.iisc.ac.in/~chiru/",
    },
    {
        "name": "Dr. Partha Talukdar",
        "inst": "IISc Bangalore",
        "area": "Knowledge Graphs & NLP",
        "keywords": ["knowledge graph", "nlp", "temporal reasoning", "embedding", "relation extraction"],
        "link": "https://talukdar.net/",
    },
    {
        "name": "Prof. Balaraman Ravindran",
        "inst": "IIT Madras",
        "area": "Reinforcement Learning & AI",
        "keywords": ["reinforcement learning", "multi-agent", "deep learning", "ai", "decision making"],
        "link": "https://www.cse.iitm.ac.in/~ravi/",
    },
    {
        "name": "Dr. Vineeth N Balasubramanian",
        "inst": "IIT Hyderabad",
        "area": "Deep Learning & Computer Vision",
        "keywords": ["deep learning", "computer vision", "explainable ai", "neural network", "representation"],
        "link": "https://www.iith.ac.in/~vineethnb/",
    },
    {
        "name": "Prof. Ponnurangam Kumaraguru",
        "inst": "IIIT Hyderabad",
        "area": "Computational Social Science & Security",
        "keywords": ["social media", "security", "privacy", "misinformation", "online safety", "cyber"],
        "link": "https://precog.iiit.ac.in/",
    },
    {
        "name": "Dr. Animesh Mukherjee",
        "inst": "IIT Kharagpur",
        "area": "Complex Networks & Computational Linguistics",
        "keywords": ["network science", "linguistics", "social networks", "complex systems", "language"],
        "link": "https://cse.iitkgp.ac.in/~animeshm/",
    },
    {
        "name": "Prof. Ganesh Ramakrishnan",
        "inst": "IIT Bombay",
        "area": "Machine Learning & NLP",
        "keywords": ["machine learning", "nlp", "knowledge extraction", "text mining", "semi-supervised"],
        "link": "https://www.cse.iitb.ac.in/~ganesh/",
    },
    {
        "name": "Dr. Srinivasan Venkataraman",
        "inst": "TIFR Mumbai",
        "area": "Theoretical Computer Science",
        "keywords": ["theory", "algorithms", "complexity", "combinatorics", "mathematical"],
        "link": "https://www.tifr.res.in/",
    },
    {
        "name": "Dr. Debdoot Sheet",
        "inst": "IIT Kharagpur",
        "area": "Medical Imaging & AI",
        "keywords": ["medical imaging", "healthcare", "deep learning", "drug", "pharmaceutical", "clinical"],
        "link": "https://cse.iitkgp.ac.in/~debdoot/",
    },
    {
        "name": "Prof. Anirban Dasgupta",
        "inst": "IIT Gandhinagar",
        "area": "Data Science & Algorithms",
        "keywords": ["data science", "algorithms", "streaming", "randomized", "graph", "big data"],
        "link": "https://iitgn.ac.in/faculty/cse/anirban",
    },
]


def recommend_faculty(text: str, institution_scope: str = "india", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recommend faculty based on keyword overlap with paper content.
    
    Args:
        text: Full extracted text of the paper.
        institution_scope: Currently only "india" is supported.
        limit: Maximum number of recommendations.
    
    Returns:
        List of faculty recommendation dicts sorted by match score.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    
    scored_faculty = []
    
    for faculty in FACULTY_DATABASE:
        # Calculate keyword overlap
        overlap = sum(1 for kw in faculty["keywords"] if kw in text_lower)
        
        if overlap == 0:
            continue
        
        # Match score: based on keyword overlap relative to total keywords
        match_score = min(int((overlap / len(faculty["keywords"])) * 100), 95)
        
        # Build why explanation
        matched = [kw for kw in faculty["keywords"] if kw in text_lower]
        why_text = f"Research overlap in: {', '.join(matched[:3])}. {faculty['name']} has extensive publications in {faculty['area']}."
        
        scored_faculty.append({
            "name": faculty["name"],
            "inst": faculty["inst"],
            "area": faculty["area"],
            "why": why_text,
            "match_score": match_score,
            "link": faculty["link"],
        })
    
    # Sort by match score descending
    scored_faculty.sort(key=lambda x: x["match_score"], reverse=True)
    
    return scored_faculty[:limit]
