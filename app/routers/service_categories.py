from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ServiceCategoryCreate
from app.service_managers.service_categories_manager import (
    ServiceCategoriesManagerAsync,
)

router = APIRouter(prefix="/service-categories", tags=["service-categories"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service_category(
    payload: ServiceCategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await ServiceCategoriesManagerAsync.create_service_category(db, payload)
    return result


@router.get("/")
async def list_service_categories(
    db: AsyncSession = Depends(get_db),
):
    categories = await ServiceCategoriesManagerAsync.get_all_service_categories(db)
    return categories


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await ServiceCategoriesManagerAsync.delete_service_category(
        db, category_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service category not found"
        )

    return None
