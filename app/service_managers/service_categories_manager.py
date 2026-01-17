from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ServiceCategory
from app.schemas import (
    ServiceCategoryCreate,
    ServiceCategoryUpdate,
    ServiceCategoryResponse
)


class ServiceCategoriesManagerAsync:
    
    @classmethod
    async def create_service_category(cls, db: AsyncSession, payload: ServiceCategoryCreate):
        name = payload.name
        metadata = payload.meta
        description = payload.description
        short_desc = payload.short_desc
        
        stmt = select(ServiceCategory).filter(ServiceCategory.name == name)
        result = await db.execute(stmt)
        existing_service = result.scalar_one_or_none()
        
        if existing_service:
            existing_service.meta = metadata
            existing_service.description = description
            existing_service.short_desc = short_desc
            await db.commit()
            await db.refresh(existing_service)
            return {"msg": "Service Category updated", "id": existing_service.id}
        
        # Create new category
        new_category = ServiceCategory(
            name=name,
            short_desc=short_desc,
            description=description,
            meta=metadata
        )
        
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        
        return {"msg": "Category successfully created", "id": new_category.id}
    
    @classmethod
    async def get_service_category(cls, db: AsyncSession, category_id: int):
        stmt = select(ServiceCategory).filter(ServiceCategory.id == category_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_all_service_categories(
        cls, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ):
        stmt = select(ServiceCategory).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @classmethod
    async def delete_service_category(cls, db: AsyncSession, category_id: int):

        category = await cls.get_service_category(db, category_id)
        
        if not category:
            return False
        
        await db.delete(category)
        await db.commit()
        
        return True