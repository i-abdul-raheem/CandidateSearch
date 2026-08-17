from pathlib import Path

from langchain_core.documents import Document

from src.ingest.data_loader import DataLoader
from src.ingest.pdf_parser import clean_resume_text


def test_clean_resume_text_normalizes_whitespace() -> None:
    assert clean_resume_text(" A  B \\n C\n\n\nD ") == "A B\nC\n\nD"


def test_split_documents_recognizes_sections(tmp_path: Path) -> None:
    loader = DataLoader(tmp_path)
    document = Document(
        page_content="SKILLS\nPython, FastAPI, PostgreSQL and Docker\nEXPERIENCE\nBuilt production APIs for several years.",
        metadata={"source": "candidate", "resume_id": "abc"},
    )
    chunks = loader.split_documents([document])
    assert [chunk.metadata["chunk_type"] for chunk in chunks] == ["skills", "experience"]


def test_split_documents_falls_back_for_unstructured_resume(tmp_path: Path) -> None:
    loader = DataLoader(tmp_path)
    document = Document(page_content="Experienced Python developer " * 10, metadata={"source": "x"})
    chunks = loader.split_documents([document])
    assert chunks
    assert chunks[0].metadata["chunk_type"] == "other"
