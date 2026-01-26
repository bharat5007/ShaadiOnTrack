from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from app.service_managers.s3_manager import S3Manager
from app.utils import require_auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(prefix="/storage", tags=["storage"])

class FileRequest(BaseModel):
    file_name: str
    content_type: str
    file_size: int
    vendor_id: Optional[int] = None

class BatchRequest(BaseModel):
    files: List[FileRequest]
    vendor_id: Optional[int] = None

@router.post("/upload-url")
@require_auth
async def get_upload_url(request: Request, payload: FileRequest, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    return await S3Manager.generate_presigned_url(
        payload.file_name,
        payload.content_type,
        payload.file_size,
        user,
        db
    )

@router.post("/upload-urls")
@require_auth
async def get_batch_upload_urls(request: Request, payload: BatchRequest, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    urls = [
        await S3Manager.generate_presigned_url(
            f.file_name,
            f.content_type,
            f.file_size,
            user,
            db
        )
        for f in payload.files
    ]
    return {"urls": urls}