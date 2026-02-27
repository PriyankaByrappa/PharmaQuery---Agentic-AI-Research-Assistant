"""Document Analysis Service — PDF text extraction and preprocessing."""
import io
from typing import Dict, Any, Optional


async def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file.
    
    Returns:
        Dict with 'text', 'page_count', 'metadata', and 'sections'.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("PyMuPDF is not installed. Run: pip install PyMuPDF")

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    full_text = ""
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")
        pages.append(page_text)
        full_text += page_text + "\n"
    
    # Extract metadata
    metadata = doc.metadata or {}
    
    # Detect sections by looking for common academic headings
    sections = detect_sections(full_text)
    
    doc.close()
    
    return {
        "text": full_text.strip(),
        "page_count": len(pages),
        "pages": pages,
        "metadata": {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
        },
        "sections": sections,
        "char_count": len(full_text.strip()),
        "word_count": len(full_text.split()),
    }


def detect_sections(text: str) -> Dict[str, Optional[str]]:
    """Detect common academic paper sections in the text."""
    import re
    
    section_patterns = [
        ("abstract", r"(?i)\b(?:abstract)\b"),
        ("introduction", r"(?i)\b(?:introduction|1\.\s*introduction)\b"),
        ("methodology", r"(?i)\b(?:method(?:ology|s)?|2\.\s*method(?:ology|s)?|approach|experimental\s+setup)\b"),
        ("results", r"(?i)\b(?:results?|3\.\s*results?|findings|experimental\s+results?)\b"),
        ("discussion", r"(?i)\b(?:discussion|4\.\s*discussion)\b"),
        ("conclusion", r"(?i)\b(?:conclusion|5\.\s*conclusion|concluding\s+remarks|summary)\b"),
        ("references", r"(?i)\b(?:references|bibliography|works\s+cited)\b"),
    ]
    
    sections = {}
    for name, pattern in section_patterns:
        match = re.search(pattern, text)
        if match:
            sections[name] = "found"
        else:
            sections[name] = None
    
    return sections


async def extract_text_from_docx(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text from a DOCX file (optional support).
    Falls back gracefully if python-docx is not installed.
    """
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    
    doc = Document(io.BytesIO(file_bytes))
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    sections = detect_sections(full_text)
    
    return {
        "text": full_text.strip(),
        "page_count": 0,  # DOCX doesn't have fixed pages
        "pages": [],
        "metadata": {
            "title": doc.core_properties.title or "",
            "author": doc.core_properties.author or "",
            "subject": doc.core_properties.subject or "",
            "keywords": doc.core_properties.keywords or "",
        },
        "sections": sections,
        "char_count": len(full_text.strip()),
        "word_count": len(full_text.split()),
    }
