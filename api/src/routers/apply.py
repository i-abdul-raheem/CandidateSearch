import uuid

from langchain_core.documents import Document
from fastapi import APIRouter, File, UploadFile, HTTPException
from src.container import get_service_container
from pathlib import Path

router = APIRouter(tags=['apply'])

@router.post("/apply")
async def apply_job(
    file: UploadFile = File(...)
) -> dict[str, str | Document]:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    service_container = get_service_container()
    loader = service_container.get_data_loader
    em = service_container.get_embedding_manager
    vs = service_container.get_vector_store
    destination_path = Path("data/pdf/uploads") / (uuid.uuid4().hex + ".pdf")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("wb") as f:
        f.write(await file.read())
        f.close()
    docs = loader.load_document(destination_path)
    chunks = loader.split_documents(docs)
    embedded_list = em.generate_embeddings(chunks)
    vs.add_documents(embedded_list)
    return {
        'message': 'Resume uploaded successfully.'
    }
