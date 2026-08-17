from fastapi import APIRouter, Depends, HTTPException, Response, status
from starlette.concurrency import run_in_threadpool

from src.container import get_service_container
from src.schemas import Role, RoleInput
from src.security import require_api_key


router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[Role])
async def list_roles() -> list[dict]:
    return await run_in_threadpool(get_service_container().get_metadata_store.list_roles)


@router.post("", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(payload: RoleInput) -> dict:
    return await run_in_threadpool(get_service_container().get_metadata_store.create_role, payload.model_dump())


@router.put("/{role_id}", response_model=Role)
async def update_role(role_id: str, payload: RoleInput) -> dict:
    role = await run_in_threadpool(get_service_container().get_metadata_store.update_role, role_id, payload.model_dump())
    if role is None:
        raise HTTPException(404, "Role not found")
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str) -> Response:
    deleted = await run_in_threadpool(get_service_container().get_metadata_store.delete_role, role_id)
    if not deleted:
        raise HTTPException(404, "Role not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
