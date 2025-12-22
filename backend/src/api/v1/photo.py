from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer

from ..deps import get_s3_service, get_session
from ...db import get_db
from ...models import User
from ...services import S3SecureService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/photo', tags=['Photo'])


@router.post('/upload', response_class=JSONResponse)
async def upload_profile_photo(
    photo: UploadFile = File(...),
    s3_service: S3SecureService = Depends(get_s3_service),
    session: SessionContainer = Depends(get_session),
    db: Session = Depends(get_db)
):
    """
    Upload a profile photo for the authenticated user.
    The photo will be stored as photo/{user_id}.{extension}
    """
    try:
        # Get user from session
        supertokens_user_id = session.get_user_id()
        
        user: User | None = db.query(User).filter(
            User.supertokens_user_id == supertokens_user_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        
        # Read the file content
        photo_data = await photo.read()
        
        # Get content type from uploaded file
        content_type = photo.content_type or 'image/png'
        
        # Upload to S3
        result = s3_service.upload_profile_photo(str(user.id), photo_data, content_type)
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error uploading profile photo: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to upload profile photo: {str(e)}'
        )
