from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ServiceCategory, Vendor, VendorMedia
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload


class VendorManager:
    
    @classmethod
    async def create_vendor(cls, db: AsyncSession, payload):
        name = payload.get("name")
        phone1 = payload.get("phone1")
        phone2 = payload.get("phone2")
        email = payload.get("email")
        metadata = payload.get("metadata")
        service_type = payload.get("service_type")
        
        stmt = select(ServiceCategory).filter(ServiceCategory.name == service_type)
        service_category = await db.execute(stmt)
        
        if not service_category:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Service Category",
                )
                
        service_id = service_category.id
        
        new_category = Vendor(
            name=name,
            phone1=phone1,
            phone2=phone2,
            email=email,
            metadata=metadata,
        )
        
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
        
        return {"msg": "Category successfully created", "id": new_category.id}
    
    # @classmethod
    # async def update_vendor_media(cls, db: AsyncSession, payload)
    
    @classmethod
    async def get_vendors(cls, db: AsyncSession, params: dict):
        skip = params.get("skip", 0)
        limit = params.get("limit", 25)
        service_name = params.get("service_name")
        name = params.get("name")
        
        query = select(Vendor).options(selectinload(Vendor.vendor_media))
        
        # Filter by service category name if provided
        if service_name:
            query = query.join(
                ServiceCategory, 
                Vendor.service_categories == ServiceCategory.id
            ).filter(ServiceCategory.name.ilike(f"%{service_name}%"), Vendor.is_active == True)
        
        # Filter by vendor name if provided
        if name:
            query = query.filter(Vendor.name.ilike(f"%{name}%"))
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        vendors = result.scalars().all()
        
        vendors_with_media = []
        for vendor in vendors:
            vendor_dict = {
                "id": vendor.id,
                "name": vendor.name,
                "phones": vendor.phones,
                "address": vendor.address,
                "emails": vendor.emails,
                "metadatas": vendor.metadatas,
                "service_categories": vendor.service_categories,
                "created_at": vendor.created_at,
                "updated_at": vendor.updated_at,
                "vendor_media": [
                    {
                        "id": media.id,
                        "media_type": media.media_type,
                        "type": media.type,
                        "created_at": media.created_at,
                        "updated_at": media.updated_at
                    }
                    for media in vendor.vendor_media
                ]
            }
            vendors_with_media.append(vendor_dict)
        
        return vendors_with_media
    
    @classmethod
    async def fetch_vendor(cls, db: AsyncSession, payload: dict):
        name = payload.get("name")
        id = payload.get("id")

        if not (name or id):
            return {"msg": "Name/Id missing"}
        
        query = select(Vendor)
        if name:
            query = query.filter(Vendor.name == name, Vendor.is_active == True)
        else:
            query.filter(Vendor.id == id)
        
        vendor = await db.execute(query)
        return vendor
    
    @classmethod
    async def update_vendor(cls, db: AsyncSession, payload: dict):
        vendor = await cls.fetch_vendor(db, payload)
        if not vendor:
            return {"msg": f"No vendor found"}
        
        metadata = payload.get("metadata", {})
        if metadata.get("phone1"):
            vendor.phone1 = metadata.get("phone1")
        
        if metadata.get("phone2"):
            vendor.phone2 = metadata.get("phone2")
        
        if metadata.get("email"):
            vendor.email = metadata.get("email")
            
        if metadata.get("metadata"):
            vendor.metadata = metadata.get("metadata")
            
        await db.commit()
        await db.refresh(vendor)
        
        return {"msg": "Vendor successfully updated"}
    
    @classmethod
    async def vendor_deactivate(cls, db: AsyncSession, params: dict):
        vendor = await cls.fetch_vendor(db, params)
        if not vendor:
            return {"msg": f"No vendor found"}
        
        vendor.is_active = False
        await db.commit()
        await db.refresh(vendor)
        
        return {"msg": "Vendor deactivated"}