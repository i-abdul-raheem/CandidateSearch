from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from starlette.concurrency import run_in_threadpool

from src.container import get_service_container
from src.schemas import RecentSearch
from src.security import require_api_key


router = APIRouter(prefix="/searches", tags=["searches"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[RecentSearch])
async def list_searches(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    return await run_in_threadpool(get_service_container().get_metadata_store.list_searches, limit)


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(search_id: str) -> Response:
    deleted = await run_in_threadpool(get_service_container().get_metadata_store.delete_search, search_id)
    if not deleted:
        raise HTTPException(404, "Search not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_searches() -> Response:
    await run_in_threadpool(get_service_container().get_metadata_store.clear_searches)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
