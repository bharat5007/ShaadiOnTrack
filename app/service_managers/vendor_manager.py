from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ServiceCategory, Vendor, VendorMedia
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from app.schemas import VendorQueryParams, VendorCreate, VendorUpdate, VendorDeactivate
from app.service.auth import AuthServiceClient
from app.utils import SharedContext
from typing import Optional


class VendorManager:
    @classmethod
    async def create_vendor(
        cls, db: AsyncSession, payload: VendorCreate, user: SharedContext
    ):
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
        service_type = payload.service_type

        stmt = select(ServiceCategory).filter(ServiceCategory.id == int(service_type))
        service_category = await db.execute(stmt)
        service_category = service_category.scalar_one_or_none()

        if not service_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
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

        # Return vendor data in same format as get_vendors
        return {
            "id": new_category.id,
            "name": new_category.name,
            "phone1": new_category.phone1,
            "phone2": new_category.phone2,
            "city": new_category.city,
            "district": new_category.district,
            "address": new_category.address,
            "lower_range": new_category.lower_range,
            "upper_range": new_category.upper_range,
            "email": new_category.email,
            "meta": new_category.meta,
            "created_at": new_category.created_at,
            "updated_at": new_category.updated_at,
            "service_category": {
                "id": service_category.id,
                "name": service_category.name,
            },
            "vendor_media": [],  # New vendor has no media yet
        }

    # @classmethod
    # async def update_vendor_media(cls, db: AsyncSession, payload)

    @classmethod
    async def get_vendors(
        cls,
        db: AsyncSession,
        params: Optional[VendorQueryParams] = None,
        user: Optional[SharedContext] = None,
    ):
        skip = params.skip if params else 0
        limit = params.limit if params else 1

        service_name = getattr(params, "service_name", None)
        name = getattr(params, "name", None)
        service_id = getattr(params, "service_id", None)
        vendor_id = getattr(params, "vendor_id", None)
        city = getattr(params, "city", None)
        district = getattr(params, "district", None)
        min_price = getattr(params, "min_price", None)
        max_price = getattr(params, "max_price", None)

        # Extract user_id from user context
        user_id = str(user.user_id) if user and user.user_id else None

        query = select(Vendor).options(
            selectinload(Vendor.vendor_media), selectinload(Vendor.service_category)
        )

        # Always filter for active vendors
        query = query.filter(Vendor.is_active)

        # Filter by service category name if provided (resolves to service_id)
        if service_name:
            stmt = select(ServiceCategory).filter(ServiceCategory.name == service_name)
            service_category = await db.execute(stmt)
            service_category = service_category.scalar_one_or_none()

            if not service_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No service category found for: {service_name}",
                )
            service_id = service_category.id

        # Accumulate filters - apply each filter if parameter is provided
        if name:
            query = query.filter(Vendor.name.ilike(f"%{name}%"))

        if service_id:
            query = query.filter(Vendor.service_category_id == service_id)

        if vendor_id:
            query = query.filter(Vendor.id == vendor_id)

        if user_id:
            query = query.filter(Vendor.username == user_id)

        if city:
            query = query.filter(Vendor.city == city)

        if district:
            query = query.filter(Vendor.district == district)

        if min_price:
            query = query.filter(Vendor.lower_range == int(min_price))

        if max_price:
            query = query.filter(Vendor.upper_range == int(max_price))

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
                }
                if vendor.service_category
                else None,
                "vendor_media": [
                    {
                        "id": media.id,
                        "media_type": media.media_type,
                        "url": media.url,
                        # "created_at": media.created_at,
                    }
                    for media in vendor.vendor_media
                ],
            }
            vendors_with_media.append(vendor_dict)

        return vendors_with_media

    @classmethod
    async def fetch_vendor(
        cls, db: AsyncSession, name: Optional[str] = None, id: Optional[int] = None
    ):
        if not (name or id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Name/Id is missing"
            )

        query = select(Vendor)
        if id:
            query = query.filter(Vendor.username == str(id), Vendor.is_active)
        else:
            query = query.filter(Vendor.name == name, Vendor.is_active)

        result = await db.execute(query)
        vendor = result.scalars().all() if result else None
        return vendor

    @classmethod
    async def update_vendor(
        cls, db: AsyncSession, payload: VendorUpdate, user: SharedContext
    ):
        user_id = user.user_id
        vendor_data = await cls.fetch_vendor(db=db, id=user_id)
        if not vendor_data:
            raise HTTPException(status_code=404, detail="Vendor not found")

        vendor = vendor_data[0]

        update_data = payload.model_dump(exclude_unset=True, exclude={"id"})
        for field, value in update_data.items():
            if hasattr(vendor, field):
                setattr(vendor, field, value)

        await db.commit()
        await db.refresh(vendor)

        return {"msg": "Vendor successfully updated"}

    @classmethod
    async def vendor_deactivate(cls, db: AsyncSession, params: VendorDeactivate):
        vendor_data = await cls.fetch_vendor(db=db, id=params.id)
        if not vendor_data:
            return {"msg": "No vendor found"}

        vendor = vendor_data[0]
        vendor.is_active = False
        await db.commit()
        await db.refresh(vendor)

        return {"msg": "Vendor deactivated"}

    @classmethod
    async def update_vendor_media(
        cls, db: AsyncSession, media_items: list, user: SharedContext
    ):
        user_id = user.user_id

        query = select(Vendor).filter(Vendor.username == str(user_id), Vendor.is_active)
        result = await db.execute(query)
        vendor = result.scalars().first() if result else None

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor not found for user: {user_id}",
            )

        vendor_id = vendor.id

        # Create vendor media records for each item
        created_media = []
        for item in media_items:
            meta = {"file_name": item["file_name"], "file_size": item["file_size"]}
            content_type = (
                "image" if item["content_type"].startswith("image/") else "video"
            )

            vendor_media = VendorMedia(
                vendor_id=vendor_id,
                media_type=content_type,
                meta=meta,
                url=item["public_url"],
            )
            db.add(vendor_media)
            created_media.append(vendor_media)

        await db.commit()

        # Refresh all created media records
        for media in created_media:
            await db.refresh(media)

        return {
            "message": "Vendor media updated successfully",
            "vendor_id": vendor_id,
            "media_count": len(created_media),
        }
