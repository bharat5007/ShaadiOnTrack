from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.service_managers.s3_manager import S3Manager

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
async def get_upload_url(request: FileRequest):
    return S3Manager.generate_presigned_url(request.file_name, request.content_type, request.vendor_id)

@router.post("/upload-urls")
async def get_batch_upload_urls(request: BatchRequest):
    urls = [
        S3Manager.generate_presigned_url(f.file_name, f.content_type, request.vendor_id or f.vendor_id)
        for f in request.files
    ]
    return {"urls": urls}