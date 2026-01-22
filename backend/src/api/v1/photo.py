from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer

from ..deps import get_s3_service, get_session, get_current_user
from ...db import get_db
from ...models import User
from ...services import S3SecureService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/photo', tags=['Photo'])


@router.get('/upload-url', response_class=JSONResponse)
async def get_photo_upload_url(
    content_type: str = Query(default='image/png', description='MIME type of the image (image/png or image/jpeg)'),
    s3_service: S3SecureService = Depends(get_s3_service),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a presigned URL for uploading a profile photo.
    Client can then PUT the photo directly to this URL.
    """
    try:
        # Validate content type
        if content_type not in ['image/png', 'image/jpeg', 'image/jpg']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid content type. Must be image/png or image/jpeg'
            )
        
        # Get presigned upload URL
        result = s3_service.get_photo_upload_url(str(user.id), content_type)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error generating upload URL: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to generate upload URL: {str(e)}'
        )


@router.get('/download-url', response_class=JSONResponse)
async def get_photo_download_url(
    s3_service: S3SecureService = Depends(get_s3_service),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a presigned URL for downloading the authenticated user's profile photo.
    """
    try:
        # Get presigned download URL
        result = s3_service.get_photo_read_url(str(user.id))
        
        if result.get('download_url') is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Profile photo not found'
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error generating download URL: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to generate download URL: {str(e)}'
        )


@router.post('/upload', response_class=JSONResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    s3_service: S3SecureService = Depends(get_s3_service),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile photo via backend (avoids CORS issues with direct S3 uploads).
    Accepts multipart/form-data with field name 'file'. Returns the S3 key and a presigned download URL.
    """
    try:
        content_type = file.content_type or 'image/png'
        if content_type not in ['image/png', 'image/jpeg', 'image/jpg']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid content type. Must be image/png or image/jpeg'
            )

        data = await file.read()
        result = s3_service.upload_profile_photo(str(user.id), photo_data=data, content_type=content_type)

        # Get presigned download URL for the uploaded photo
        read = s3_service.get_photo_read_url(str(user.id))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'message': 'ok',
                'key': result.get('key'),
                'download_url': read.get('download_url')
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error uploading profile photo: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to upload profile photo: {str(e)}'
        )
