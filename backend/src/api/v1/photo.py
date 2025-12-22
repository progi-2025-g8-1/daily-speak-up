from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..deps import get_s3_service
from ...services import S3SecureService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/photo', tags=['Photo'])


@router.post('/upload/{user_id}', response_class=JSONResponse)
async def upload_profile_photo(
    user_id: str,
    photo: UploadFile = File(...),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    try:
        # Read the file content
        photo_data = await photo.read()
        
        # Get content type from uploaded file
        content_type = photo.content_type or 'image/png'
        
        # Upload to S3
        result = s3_service.upload_profile_photo(user_id, photo_data, content_type)
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    
    except Exception as e:
        logger.error(f'Error uploading profile photo for user {user_id}: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to upload profile photo: {str(e)}'
        )
