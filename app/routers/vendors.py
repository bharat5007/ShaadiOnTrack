from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    VendorUpdate,
    VendorQueryParams,
    VendorCreate,
    VendorDeactivate,
    UpdateMediaRequest,
    DeleteMedia
)
from app.service_managers.vendor_manager import VendorManager
from app.utils import require_auth

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@require_auth
async def create_vendor(
    request: Request,
    payload: VendorCreate,
    db: Session = Depends(get_db),
):
    user = request.state.user
    result = await VendorManager.create_vendor(db=db, payload=payload, user=user)
    return result


@router.get("/")
# @require_auth
async def list_vendors(
    request: Request,
    params: VendorQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    # user = request.state.user
    vendors = await VendorManager.get_vendors(
        db=db, 
        params=params
    )
    return vendors


@router.get("/user_id")
@require_auth
async def list_vendors(
    request: Request,
    params: VendorQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    user = request.state.user
    vendors = await VendorManager.get_vendors(
        db=db, 
        user=user
    )
    return vendors


@router.put("/update")
@require_auth
async def update_vendor(
    request: Request,
    payload: VendorUpdate,
    db: Session = Depends(get_db),
):
    user = request.state.user
    response = await VendorManager.update_vendor(db=db, payload=payload, user=user)
    return response

@router.put("/deactivate")
async def deactivate_vendor(
    params: VendorDeactivate = Depends(),
    db: Session = Depends(get_db),
):
    response = await VendorManager.vendor_deactivate(db=db, params=params.model_dump())
    return response


@router.post("/update_media", status_code=status.HTTP_200_OK)
@require_auth
async def update_vendor_media(
    request: Request,
    payload: UpdateMediaRequest,
    db: Session = Depends(get_db)
):
    user = request.state.user
    media_items = [item.model_dump() for item in payload.media]
    result = await VendorManager.update_vendor_media(
        db=db,
        media_items=media_items,
        user=user
    )
    return result