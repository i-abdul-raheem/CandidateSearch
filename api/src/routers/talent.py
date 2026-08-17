from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from starlette.concurrency import run_in_threadpool

from src.config import settings
from src.container import get_service_container
from src.schemas import TalentCandidate, TalentPoolResponse
from src.security import require_api_key


router = APIRouter(prefix="/talent", tags=["talent"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=TalentPoolResponse)
async def list_talent(
    request: Request,
    search: str = Query(default="", max_length=500),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> TalentPoolResponse:
    store = get_service_container().get_vector_store
    result = await run_in_threadpool(store.collection.get, include=["metadatas"])
    grouped: dict[str, dict] = {}
    for metadata in result.get("metadatas") or []:
        if not metadata or not metadata.get("resume_id"):
            continue
        internal_id = str(metadata["resume_id"])
        public_id = store.public_resume_id(internal_id)
        item = grouped.setdefault(public_id, {
            "resume_id": public_id,
            "filename": str(metadata.get("filename") or Path(internal_id).name),
            "sections": set(),
        })
        item["sections"].add(str(metadata.get("chunk_type", "other")))

    query = search.casefold().strip()
    candidates = [item for item in grouped.values() if not query or query in item["filename"].casefold()]
    candidates.sort(key=lambda item: item["filename"].casefold())
    total = len(candidates)
    page = candidates[offset:offset + limit]
    return TalentPoolResponse(results=[TalentCandidate(
        resume_id=item["resume_id"],
        resume_url=str(request.url_for("get_resume_file", resume_id=item["resume_id"])),
        filename=item["filename"],
        sections=sorted(item["sections"]),
    ) for item in page], total=total)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_talent(resume_id: str) -> Response:
    store = get_service_container().get_vector_store
    internal_id = store.resolve_resume_id(resume_id)
    if internal_id is None:
        raise HTTPException(404, "Candidate not found")
    await run_in_threadpool(store.delete_resume, internal_id)
    if internal_id == resume_id:
        (settings.upload_dir / f"{resume_id}.pdf").unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
