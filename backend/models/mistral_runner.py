import logging

from llama_cpp import Llama
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt', quiet=True)

logger = logging.getLogger(__name__)

# Characters of prompt text kept per chunk — well within Gemma 3 1B context
MAX_CHUNK_TOKENS = 1200
# Tokens the model is allowed to generate per answer
MAX_NEW_TOKENS = 700

llm = Llama(
    model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,       # larger context → fewer truncation issues
    n_threads=4,
    n_gpu_layers=0,
    use_mlock=False,
    verbose=False,    # silence per-token noise in the console
)


def count_tokens(text: str) -> int:
    """Rough word-based token estimate (good enough for chunk splitting)."""
    return len(text.split())


def split_prompt_into_chunks(prompt: str, max_tokens: int = MAX_CHUNK_TOKENS) -> list[str]:
    """Split a long prompt into sentence-aligned chunks that fit in context."""
    sentences = sent_tokenize(prompt)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        t = count_tokens(sentence)
        if current_tokens + t > max_tokens and current:
            chunks.append(' '.join(current))
            current = [sentence]
            current_tokens = t
        else:
            current.append(sentence)
            current_tokens += t

    if current:
        chunks.append(' '.join(current))

    return chunks


def generate_answer(prompt: str) -> str:
    """
    Send prompt to the local Gemma model using the chat-completion API,
    which applies the correct instruct format automatically.
    Returns the full generated text without truncation.
    """
    chunks = split_prompt_into_chunks(prompt)
    responses: list[str] = []

    for chunk in chunks:
        try:
            output = llm.create_chat_completion(
                messages=[{"role": "user", "content": chunk}],
                max_tokens=MAX_NEW_TOKENS,
                temperature=0.1,
                repeat_penalty=1.1,
            )
            text = output["choices"][0]["message"]["content"].strip()
            responses.append(text)
        except Exception as exc:
            logger.exception("LLM inference failed: %s", exc)
            responses.append("[Error generating answer]")

    return ' '.join(responses)
