from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from src.config import settings
from src.container import get_service_container
from src.security import require_api_key


router = APIRouter(tags=["files"], dependencies=[Depends(require_api_key)])


@router.get(
    "/file/{resume_id}",
    name="get_resume_file",
    response_class=FileResponse,
    responses={404: {"description": "Resume not found"}},
)
async def get_resume_file(resume_id: str) -> FileResponse:
    vector_store = get_service_container().get_vector_store
    internal_id = vector_store.resolve_resume_id(resume_id)
    if internal_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    if internal_id == resume_id:
        resume_path = settings.upload_dir / f"{resume_id}.pdf"
    else:
        source_path = Path(internal_id)
        resume_path = source_path if source_path.is_absolute() else settings.data_dir.parent / source_path
        try:
            resume_path.resolve().relative_to(settings.resume_dir.resolve())
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    if not resume_path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    return FileResponse(
        resume_path,
        media_type="application/pdf",
        filename=f"resume-{resume_id}.pdf",
        content_disposition_type="inline",
    )
