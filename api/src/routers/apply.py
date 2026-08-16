from langchain_core.documents import Document
from fastapi import APIRouter, File, UploadFile, HTTPException
from src.ingest.pdf_parser import parse_resume
from pathlib import Path
router = APIRouter(tags=['apply'])

@router.post("/")
async def apply_job(
    file: UploadFile = File(...)
) -> dict[str, str | Document]:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    doc = parse_resume(file.file.read(), isStream=True)
    return {
        'doc': doc
    }