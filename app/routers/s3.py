from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import S3UploadUrlRequest, S3UploadUrlResponse
from app.service_managers.s3_manager import S3Manager
from app.utils import require_auth

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload-url", response_model=S3UploadUrlResponse, status_code=status.HTTP_200_OK)
@require_auth
async def generate_upload_url(
    request: Request,
    payload: S3UploadUrlRequest,
    db: Session = Depends(get_db),
):
    """Generate presigned URL for uploading files to S3.
    
    This endpoint generates a temporary URL that allows direct upload to S3.
    After uploading to the URL, call the /confirm-upload endpoint to save metadata.
    
    Flow:
    1. Call this endpoint with file details
    2. Get presigned URL
    3. Upload file directly to S3 using the URL (PUT request)
    4. Call /confirm-upload with file_key to save metadata
    """
    user = request.state.user
    result = await S3Manager.generate_upload_url(db=db, payload=payload, user=user)
    return result


@router.post("/confirm-upload", status_code=status.HTTP_201_CREATED)
@require_auth
async def confirm_upload(
    request: Request,
    vendor_id: int,
    file_key: str,
    media_type: str,
    db: Session = Depends(get_db),
):
    """Confirm successful upload and save media metadata to database.
    
    Call this endpoint after successfully uploading a file to the presigned URL.
    """
    result = await S3Manager.save_vendor_media(
        db=db,
        vendor_id=vendor_id,
        file_key=file_key,
        media_type=media_type
    )
    return {
        "msg": "Media uploaded successfully",
        "media_id": result.id,
        "url": result.url
    }