import pdfplumber
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt')

MAX_TOKENS = 1800  # Adjust for your model context window safely


def count_tokens(text: str) -> int:
    # Rough token count approximation
    return len(text.split())


def split_text_to_chunks(text: str, max_tokens=MAX_TOKENS) -> list[str]:
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + ' '
    return text.strip()
