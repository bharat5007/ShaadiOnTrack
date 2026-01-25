import boto3
import logging
import uuid
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling S3 operations."""

    def __init__(self):
        """Initialize S3 client with credentials from settings."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
            self.expiry = settings.S3_PRESIGNED_URL_EXPIRY
        except Exception as e:
            logger.exception("Failed to initialize S3 client")
            raise HTTPException(status_code=500, detail="S3 service initialization failed")

    def generate_presigned_upload_url(
        self,
        file_key: str,
        file_type: str,
        expiry: int = None
    ) -> str:
        """Generate a presigned URL for uploading a file to S3.
        
        Args:
            file_key: S3 key where the file will be stored
            file_type: MIME type of the file
            expiry: URL expiry time in seconds (defaults to settings value)
            
        Returns:
            Presigned URL string
        """
        try:
            expiry = expiry or self.expiry
            
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': file_type,
                },
                ExpiresIn=expiry,
                HttpMethod='PUT'
            )
            
            logger.info(f"Generated presigned URL for key: {file_key}")
            return presigned_url
            
        except ClientError as e:
            logger.exception(f"AWS ClientError generating presigned URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")
        except BotoCoreError as e:
            logger.exception(f"BotoCoreError generating presigned URL: {e}")
            raise HTTPException(status_code=500, detail="S3 service error")
        except Exception as e:
            logger.exception(f"Unexpected error generating presigned URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate upload URL")

    def generate_presigned_download_url(self, file_key: str, expiry: int = 3600) -> str:
        """Generate a presigned URL for downloading a file from S3.
        
        Args:
            file_key: S3 key of the file
            expiry: URL expiry time in seconds
            
        Returns:
            Presigned URL string
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                },
                ExpiresIn=expiry
            )
            
            return presigned_url
            
        except Exception as e:
            logger.exception(f"Error generating download URL: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate download URL")

    def get_public_url(self, file_key: str) -> str:
        """Get public URL for a file (if bucket is public).
        
        Args:
            file_key: S3 key of the file
            
        Returns:
            Public URL string
        """
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"