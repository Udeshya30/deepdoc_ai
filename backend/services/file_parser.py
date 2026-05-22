import fitz  # PyMuPDF
import docx
import io

def parse_file(content: bytes, filename: str) -> str:
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file type."
