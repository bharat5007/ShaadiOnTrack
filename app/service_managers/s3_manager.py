import boto3
from botocore.config import Config
from app.config import settings
import uuid


class S3Manager:

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=Config(signature_version='s3v4')
    )

    @classmethod
    def generate_presigned_url(cls, file_name: str, content_type: str, vendor_id: int = None):
        # Create organized key path
        unique_id = uuid.uuid4().hex[:8]
        if vendor_id:
            key = f"vendors/{vendor_id}/portfolio/{unique_id}_{file_name}"
        else:
            key = f"uploads/{unique_id}_{file_name}"

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