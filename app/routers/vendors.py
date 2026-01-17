from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    VendorUpdate,
    VendorQueryParams,
    VendorCreate,
    VendorDeactivate
)
from app.service_managers.vendor_manager import VendorManager

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db),
):

    result = await VendorManager.create_vendor(db=db, payload=payload)
    return result


@router.get("/")
async def list_vendors(
    params: VendorQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    vendors = await VendorManager.get_vendors(
        db=db, 
        params=params
    )
    return vendors


@router.put("/update")
async def update_vendor(
    payload: VendorUpdate = Depends(),
    db: Session = Depends(get_db),
):

    response = await VendorManager.update_vendor(db=db, payload=payload.model_dump())
    return response

@router.put("/deactivate")
async def deactivate_vendor(
    params: VendorDeactivate = Depends(),
    db: Session = Depends(get_db),
):
    response = await VendorManager.vendor_deactivate(db=db, params=params.model_dump())
    return response