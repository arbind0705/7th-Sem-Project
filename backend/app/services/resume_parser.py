import pymupdf as fitz
import docx


def extract_text(filename: str, content: bytes) -> str:
    """Extract raw text from a PDF or DOCX resume."""
    if filename.lower().endswith(".pdf"):
        with fitz.open(stream=content, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    if filename.lower().endswith(".docx"):
        import io

        d = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in d.paragraphs)
    raise ValueError("Unsupported resume format: only .pdf and .docx are accepted")
