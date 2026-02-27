"""Research Scoring Engine — Heuristic-based quality scoring for academic papers.

Evaluates research papers across 9 IEEE-level quality dimensions using
text analysis heuristics (keyword density, structure detection, citation patterns,
readability metrics). Designed for future LLM integration.
"""
import re
import math
from typing import Dict, Any, List, Tuple


# ─── Scoring weights ───────────────────────────────────────────────────────────
DIMENSION_WEIGHTS = {
    "novelty": 1.2,
    "methodological_rigor": 1.2,
    "citation_credibility": 1.1,
    "technical_depth": 1.1,
    "mathematical_formalism": 0.9,
    "literature_coverage": 0.9,
    "structural_quality": 0.8,
    "clarity_coherence": 0.9,
    "reproducibility": 0.9,
}


# ─── Keyword sets for heuristic analysis ────────────────────────────────────────
NOVELTY_KEYWORDS = [
    "novel", "new approach", "first time", "unprecedented", "innovative",
    "we propose", "we introduce", "our contribution", "unique", "original",
    "state-of-the-art", "breakthrough", "pioneering", "emerging",
]

METHODOLOGY_KEYWORDS = [
    "methodology", "experimental", "cross-validation", "baseline",
    "ablation", "benchmark", "dataset", "evaluation metrics",
    "hyperparameter", "training", "testing", "validation set",
    "statistical significance", "p-value", "confidence interval",
    "controlled experiment", "randomized",
]

TECHNICAL_KEYWORDS = [
    "algorithm", "complexity", "optimization", "convergence",
    "gradient", "loss function", "regularization", "architecture",
    "framework", "pipeline", "inference", "latent", "embedding",
    "transformer", "attention mechanism", "convolution", "recurrent",
]

MATH_PATTERNS = [
    r"\$.*?\$",           # LaTeX inline math
    r"\\begin\{equation\}",
    r"\\sum", r"\\prod", r"\\int",
    r"\b[A-Z]\s*=\s*",    # Variable assignments
    r"\barg\s*min\b", r"\barg\s*max\b",
    r"\bp\s*\(\s*\w", r"\bP\s*\(\s*\w",  # Probability notation
    r"\b\d+\.\d+\s*[±×]\s*\d+",  # Numerical results with errors
]

HEDGING_WORDS = [
    "might", "possibly", "perhaps", "seems", "appears to",
    "could be", "may", "likely", "unlikely", "suggest",
    "it is believed", "arguably", "presumably",
]

REPRODUCIBILITY_KEYWORDS = [
    "reproducib", "open source", "github", "code available",
    "data available", "publicly available", "repository",
    "supplementary material", "appendix", "implementation details",
    "hyperparameters", "hardware", "gpu", "cpu", "training time",
]


def score_paper(text: str, sections: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Score a research paper across 9 quality dimensions.
    
    Args:
        text: Full extracted text of the paper.
        sections: Dict of detected sections (from document_analysis).
    
    Returns:
        Dict with 'total_score', 'dimensions', 'dimension_details'.
    """
    if not text or len(text.strip()) < 100:
        return _empty_score()

    text_lower = text.lower()
    word_count = len(text.split())
    sections = sections or {}

    dimensions = {}
    
    # 1. Novelty (keyword density + claim strength)
    dimensions["novelty"] = _score_novelty(text_lower, word_count)
    
    # 2. Methodological Rigor
    dimensions["methodological_rigor"] = _score_methodology(text_lower, word_count)
    
    # 3. Citation Credibility
    dimensions["citation_credibility"] = _score_citations(text, text_lower)
    
    # 4. Technical Depth
    dimensions["technical_depth"] = _score_technical_depth(text_lower, word_count)
    
    # 5. Mathematical Formalism
    dimensions["mathematical_formalism"] = _score_math(text)
    
    # 6. Literature Coverage
    dimensions["literature_coverage"] = _score_literature(text_lower, text)
    
    # 7. Structural Quality
    dimensions["structural_quality"] = _score_structure(sections)
    
    # 8. Clarity & Coherence
    dimensions["clarity_coherence"] = _score_clarity(text_lower, word_count)
    
    # 9. Reproducibility
    dimensions["reproducibility"] = _score_reproducibility(text_lower)

    # Calculate weighted total
    weighted_sum = sum(
        dimensions[dim] * DIMENSION_WEIGHTS[dim]
        for dim in dimensions
    )
    weight_total = sum(DIMENSION_WEIGHTS.values())
    total_score = weighted_sum / weight_total

    # Apply strict academic penalty — scores > 80 are extremely rare
    if total_score > 80:
        total_score = 80 + (total_score - 80) * 0.3
    if total_score > 85:
        total_score = 85  # Hard cap

    return {
        "total_score": round(total_score, 1),
        "dimensions": {k: min(v, 95) for k, v in dimensions.items()},
    }


def _empty_score() -> Dict[str, Any]:
    return {
        "total_score": 0.0,
        "dimensions": {dim: 0 for dim in DIMENSION_WEIGHTS},
    }


def _keyword_density(text: str, keywords: List[str], word_count: int) -> float:
    """Count keyword occurrences normalized by word count."""
    count = sum(1 for kw in keywords if kw in text)
    return min(count / max(len(keywords), 1) * 100, 100)


# ─── Individual dimension scorers ──────────────────────────────────────────────

def _score_novelty(text: str, word_count: int) -> int:
    density = _keyword_density(text, NOVELTY_KEYWORDS, word_count)
    base = min(30 + density * 0.5, 85)
    # Bonus for comparative statements
    if "compared to" in text or "outperforms" in text or "improvement over" in text:
        base += 5
    return int(min(base, 90))


def _score_methodology(text: str, word_count: int) -> int:
    density = _keyword_density(text, METHODOLOGY_KEYWORDS, word_count)
    base = min(25 + density * 0.6, 85)
    if "ablation study" in text or "ablation" in text:
        base += 5
    if "baseline" in text:
        base += 3
    return int(min(base, 90))


def _score_citations(text: str, text_lower: str) -> int:
    # Count citation patterns: [1], [2-5], (Author, Year), etc.
    bracket_cites = len(re.findall(r"\[\d+(?:\s*[-–,]\s*\d+)*\]", text))
    paren_cites = len(re.findall(r"\(\w+(?:\s+et\s+al\.?)?,?\s*\d{4}\)", text))
    total_cites = bracket_cites + paren_cites
    
    if total_cites == 0:
        return 20
    elif total_cites < 5:
        return 35
    elif total_cites < 15:
        return 55
    elif total_cites < 30:
        return 70
    else:
        return min(75 + total_cites // 10, 85)


def _score_technical_depth(text: str, word_count: int) -> int:
    density = _keyword_density(text, TECHNICAL_KEYWORDS, word_count)
    base = min(25 + density * 0.55, 80)
    # Boost for code snippets or pseudocode
    if "algorithm" in text and ("input" in text or "output" in text):
        base += 5
    return int(min(base, 85))


def _score_math(text: str) -> int:
    math_count = sum(len(re.findall(p, text)) for p in MATH_PATTERNS)
    if math_count == 0:
        return 20
    elif math_count < 3:
        return 40
    elif math_count < 10:
        return 60
    elif math_count < 20:
        return 72
    else:
        return min(75 + math_count // 5, 85)


def _score_literature(text: str, raw_text: str) -> int:
    # Count references section depth
    refs_match = re.search(r"(?i)references\b", raw_text)
    if not refs_match:
        return 25
    
    refs_text = raw_text[refs_match.start():]
    ref_entries = len(re.findall(r"\[\d+\]", refs_text))
    
    if ref_entries == 0:
        # Try numbered list format
        ref_entries = len(re.findall(r"\n\s*\d+\.\s+", refs_text))
    
    if ref_entries < 5:
        return 30
    elif ref_entries < 15:
        return 50
    elif ref_entries < 30:
        return 65
    else:
        return min(70 + ref_entries // 10, 85)


def _score_structure(sections: Dict[str, Any]) -> int:
    """Score based on presence of standard academic sections."""
    required = ["abstract", "introduction", "methodology", "results", "conclusion"]
    optional = ["discussion", "references"]
    
    found_required = sum(1 for s in required if sections.get(s))
    found_optional = sum(1 for s in optional if sections.get(s))
    
    base = (found_required / len(required)) * 70
    base += (found_optional / len(optional)) * 15
    base += 10  # Base score for having any structure
    
    return int(min(base, 90))


def _score_clarity(text: str, word_count: int) -> int:
    # Penalize excessive hedging
    hedge_count = sum(1 for hw in HEDGING_WORDS if hw in text)
    hedge_penalty = min(hedge_count * 3, 20)
    
    # Average sentence length (proxy for readability)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if sentences:
        avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences)
        # Ideal: 15-25 words per sentence
        if 15 <= avg_sentence_len <= 25:
            length_score = 30
        elif 10 <= avg_sentence_len <= 30:
            length_score = 20
        else:
            length_score = 10
    else:
        length_score = 10
    
    base = 40 + length_score - hedge_penalty
    return int(max(min(base, 85), 15))


def _score_reproducibility(text: str) -> int:
    density = _keyword_density(text, REPRODUCIBILITY_KEYWORDS, len(text.split()))
    base = min(20 + density * 0.6, 80)
    if "github.com" in text or "gitlab.com" in text:
        base += 10
    if "dataset" in text and ("available" in text or "download" in text):
        base += 5
    return int(min(base, 85))
