from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database_async import get_async_db
from app.auth import get_current_active_user
from app.schemas import (
    ServiceCategoryCreate,
    ServiceCategoryUpdate,
    ServiceCategoryResponse
)
from app.service_managers.service_categories_manager import ServiceCategoriesManagerAsync

router = APIRouter(prefix="/service-categories", tags=["service-categories"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service_category(
    payload: ServiceCategoryCreate,
    db: AsyncSession = Depends(get_async_db),
    # current_user: dict = Depends(get_current_active_user)
):

    result = await ServiceCategoriesManagerAsync.create_service_category(db, payload)
    return result


@router.get("/")
async def list_service_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    # current_user: dict = Depends(get_current_active_user)
):

    categories = await ServiceCategoriesManagerAsync.get_all_service_categories(db, skip, limit)
    return categories



@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
):

    deleted = await ServiceCategoriesManagerAsync.delete_service_category(db, category_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found"
        )
    
    return None