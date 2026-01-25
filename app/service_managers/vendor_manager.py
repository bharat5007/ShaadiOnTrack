from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ServiceCategory, Vendor, VendorMedia
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from app.schemas import VendorQueryParams, VendorCreate
from app.service.auth import AuthServiceClient



class VendorManager:
    
    @classmethod
    async def create_vendor(cls, db: AsyncSession, payload: VendorCreate, user: object):
        name = payload.name
        phone1 = payload.phone1
        phone2 = payload.phone2
        email = payload.email
        username = user.user_id
        lower_range = payload.lower_range
        upper_range = payload.upper_range
        address = payload.address
        city = payload.city
        district = payload.district
        metadata = payload.meta
        service_type = int(payload.service_type)
        
        stmt = select(ServiceCategory).filter(ServiceCategory.id == service_type)
        service_category = await db.execute(stmt)
        service_category = service_category.scalar_one_or_none()
        
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
            username=str(username),
            address=address,
            city=city,
            district=district,
            lower_range=lower_range,
            upper_range=upper_range,
            meta=metadata,
            service_category_id=service_id,
        )
        db.add(new_category)
        
        vendor_update_payload = {"phone": phone1}
        await AuthServiceClient.update_vendor_role(vendor_update_payload)
    
        await db.commit()
        await db.refresh(new_category)
        
        return {"msg": "Once verified you will be on the list"}
    
    # @classmethod
    # async def update_vendor_media(cls, db: AsyncSession, payload)
    
    @classmethod
    async def get_vendors(cls, db: AsyncSession, params: VendorQueryParams = None, user: object = None):
        skip = params.skip if params else 0
        limit = params.limit if params else 1
        service_name = params.service_name if params else None
        name = params.name if params else None
        service_id = int(params.service_id) if params else None
        vendor_id = int(params.vendor_id) if params else None
        user_id = str(user.user_id) if user and user.user_id else None
        
        query = select(Vendor).options(
            selectinload(Vendor.vendor_media),
            selectinload(Vendor.service_category)
        )
        
        # Filter by service category name if provided
        if service_name:
            stmt = select(ServiceCategory).filter(ServiceCategory.name == service_name)
            service_category = await db.execute(stmt)
            service_category = service_category.scalar_one_or_none()
            service_id = service_category.id
        
        # Filter by vendor name if provided
        elif name:
            query = query.filter(Vendor.name.ilike(f"%{name}%"), Vendor.is_active == True)
            
        elif service_id:
            query = query.filter(Vendor.service_category_id == service_id, Vendor.is_active == True)
            
        elif vendor_id:
            query = query.filter(Vendor.id == vendor_id, Vendor.is_active == True)
            
        elif user_id:
            query = query.filter(Vendor.username == user_id, Vendor.is_active == True)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        vendors = result.scalars().all()
        
        vendors_with_media = []
        for vendor in vendors:
            vendor_dict = {
                "id": vendor.id,
                "name": vendor.name,
                "phone1": vendor.phone1,
                "phone2": vendor.phone2,
                "city": vendor.city,
                "district": vendor.district,
                "address": vendor.address,
                "lower_range": vendor.lower_range,
                "upper_range": vendor.upper_range,
                "email": vendor.email,
                "meta": vendor.meta,
                "created_at": vendor.created_at,
                "updated_at": vendor.updated_at,
                "service_category": {
                    "id": vendor.service_category.id,
                    "name": vendor.service_category.name,
                } if vendor.service_category else None,
                "vendor_media": [
                    {
                        "id": media.id,
                        "media_type": media.media_type,
                        "url": media.url,
                        # "created_at": media.created_at,
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