import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from starlette.concurrency import run_in_threadpool
from src.container import get_service_container
from src.config import settings
from src.schemas import UploadResponse

router = APIRouter(tags=["apply"])

@router.post("/apply", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def apply_job(
    file: UploadFile = File(...)
) -> UploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    content = await file.read(settings.max_upload_bytes + 1)
    await file.close()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "PDF exceeds upload limit")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file is not a valid PDF")

    resume_id = uuid.uuid4().hex
    destination_path = settings.upload_dir / f"{resume_id}.pdf"
    container = get_service_container()
    try:
        docs = await run_in_threadpool(container.get_data_loader.load_bytes, content, resume_id)
        for doc in docs:
            doc.metadata["resume_id"] = resume_id
            doc.metadata["filename"] = file.filename or "resume.pdf"
        chunks = container.get_data_loader.split_documents(docs)
        embedded = await run_in_threadpool(container.get_embedding_manager.generate_embeddings, chunks)
        await run_in_threadpool(container.get_vector_store.add_documents, embedded)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        await run_in_threadpool(destination_path.write_bytes, content)
    except ValueError as exc:
        container.get_vector_store.delete_resume(resume_id)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except Exception:
        container.get_vector_store.delete_resume(resume_id)
        destination_path.unlink(missing_ok=True)
        raise

    return UploadResponse(message="Resume uploaded successfully.", resume_id=resume_id)
