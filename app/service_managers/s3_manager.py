import boto3
from botocore.config import Config
from app.config import settings
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Vendor, VendorMedia
from sqlalchemy import select
from fastapi import HTTPException, status
from app.schemas import DeleteMedia
from urllib.parse import urlparse

class S3Manager:

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=Config(signature_version='s3v4')
    )

    @classmethod
    async def generate_presigned_url(cls, file_name: str, content_type: str, file_size: int, user: object, db: AsyncSession):
        user_id = user.user_id
        query = select(Vendor).filter(Vendor.username == str(user_id), Vendor.is_active == True)
        result = await db.execute(query)
        vendor = result.scalars().first() if result else None
        if not vendor:
            raise HTTPException(status_code=400, detail=f"Vendor not found for user: {user_id}")
        
        vendor_id = vendor.id
        # Create organized key path
        unique_id = uuid.uuid4().hex[:8]
        key = f"vendors/{vendor_id}/portfolio/{unique_id}_{file_name}"

        url = cls.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=3600
        )

        public_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

        return {
            "upload_url": url,
            "file_key": key,
            "public_url": public_url,
            "expires_in": 3600
        }
        
    @classmethod
    async def delete_media(cls, db: AsyncSession, payload: DeleteMedia):
        public_url = payload.public_url
        parsed_url = urlparse(public_url)
        s3_key = parsed_url.path.lstrip('/')
        
        media_query = select(VendorMedia).filter(
            VendorMedia.url == public_url,
        )
        media_result = await db.execute(media_query)
        media = media_result.scalars().first()
        
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found or does not belong to this vendor"
            )
        
        cls.s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        
        await db.delete(media)
        await db.commit()
        return {"message": "Media deleted"}