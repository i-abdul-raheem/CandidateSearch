import re
import unicodedata

import pymupdf
from langchain_core.documents import Document


def clean_resume_text(text: str) -> str:
    # Convert escaped newlines when the input contains literal "\n"
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Replace non-breaking and unusual spaces
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")  # Zero-width space

    # Remove spaces around newlines
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)

    # Collapse repeated horizontal spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Keep no more than one empty line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Clean every line
    lines = [line.strip() for line in text.splitlines()]

    return "\n".join(lines).strip()

def parse_resume(path_or_bytes, is_stream: bool = False) -> Document:
    try:
        document = (
            pymupdf.open(stream=path_or_bytes, filetype="pdf")
            if is_stream
            else pymupdf.open(path_or_bytes)
        )
        with document:
            page_content = "\n".join(
                page.get_text("text", sort=True) for page in document.pages()
            )
            metadata = dict(document.metadata or {})
    except (pymupdf.FileDataError, ValueError, TypeError) as exc:
        raise ValueError("The uploaded file is not a valid PDF.") from exc

    cleaned = clean_resume_text(page_content)
    if not cleaned:
        raise ValueError("The PDF contains no extractable text.")
    return Document(page_content=cleaned, metadata=metadata)
