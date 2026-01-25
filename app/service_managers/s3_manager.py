from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models import Vendor, VendorMedia
from app.schemas import S3UploadUrlRequest, S3UploadUrlResponse
from app.service.s3 import S3Service
from datetime import datetime
import uuid


class S3Manager:
    """Manager for S3-related operations."""

    @classmethod
    async def generate_upload_url(
        cls,
        db: AsyncSession,
        payload: S3UploadUrlRequest,
        user: object
    ) -> S3UploadUrlResponse:
        """Generate presigned URL for uploading media.
        
        If vendor_id is provided, validates that the user owns the vendor.
        """
        user_id = user.user_id
        vendor_id = payload.vendor_id

        # If vendor_id provided, verify user owns the vendor
        if vendor_id:
            stmt = select(Vendor).filter(
                Vendor.id == vendor_id,
                Vendor.username == str(user_id),
                Vendor.is_active == True
            )
            result = await db.execute(stmt)
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                raise HTTPException(
                    status_code=404,
                    detail="Vendor not found or you don't have permission"
                )

        # Initialize S3 service
        s3_service = S3Service()

        # Generate unique file key
        file_key = cls.generate_file_key(
            user_id=user_id,
            vendor_id=vendor_id,
            file_name=payload.file_name,
            media_type=payload.media_type
        )

        # Generate presigned upload URL
        upload_url = s3_service.generate_presigned_upload_url(
            file_key=file_key,
            file_type=payload.file_type
        )

        # Generate public URL (where file will be accessible after upload)
        public_url = s3_service.get_public_url(file_key)

        return S3UploadUrlResponse(
            upload_url=upload_url,
            file_key=file_key,
            public_url=public_url,
            expire_in=s3_service.expiry
        )

    @classmethod
    async def save_vendor_media(
        cls,
        db: AsyncSession,
        vendor_id: int,
        file_key: str,
        media_type: str,
        meta: dict = None
    ) -> VendorMedia:
        """Save vendor media record to database after successful upload."""
        
        # Verify vendor exists
        stmt = select(Vendor).filter(Vendor.id == vendor_id)
        result = await db.execute(stmt)
        vendor = result.scalar_one_or_none()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        # Generate public/presigned URL for the uploaded file
        s3_service = S3Service()
        url = s3_service.get_public_url(file_key)

        # Create vendor media record
        vendor_media = VendorMedia(
            vendor_id=vendor_id,
            media_type=media_type,
            url=url,
            meta=meta or {"s3_key": file_key}
        )

        db.add(vendor_media)
        await db.commit()
        await db.refresh(vendor_media)

        return vendor_media
    
    def generate_file_key(self, user_id: int, vendor_id: int = None, file_name: str = None, media_type: str = None) -> str:
        """Generate a unique S3 key for the file.
        
        Format: vendors/{vendor_id}/{media_type}/{timestamp}_{uuid}_{filename}
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Sanitize filename
        safe_filename = file_name.replace(" ", "_") if file_name else "file"
        
        if vendor_id:
            key = f"vendors/{vendor_id}/{media_type}/{timestamp}_{unique_id}_{safe_filename}"
        else:
            key = f"users/{user_id}/{media_type}/{timestamp}_{unique_id}_{safe_filename}"
        
        return key