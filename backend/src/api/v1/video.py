from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from ..deps import get_session, get_s3_service, get_gemini_service
from ...models import User, Speech, UserInterest, SpeechVisibility
from ...schemas import UploadRequestResponse, VideoReadResponse
from sqlalchemy.orm import Session
from ...db import get_db
from supertokens_python.recipe.session import SessionContainer 
from ...services import S3SecureService, GeminiService
import random

router = APIRouter(prefix="/video", tags=["Video"])

@router.get('/start', response_model=UploadRequestResponse)
async def get_upload_token(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    supertokens_user_id = session.get_user_id()

    # Get user who requested to start a speech
    user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    # Ensure the user has at least a single interest and choose one
    if not user.user_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no interests selected"
        )
    
    chosen_interest = random.choice([ui.interest for ui in user.user_interests])

    # Generate a topic based on the chosen interest
    topic = await gemini_service.generate_topic(chosen_interest.name, user.preferred_lang)

    # Create a speech object - commit first to get the ID
    speech = Speech(
        user_id=user.id,
        interest_id=chosen_interest.id,
        task=topic
    )
    db.add(speech)
    db.commit()
    db.refresh(speech)
    
    # Now generate presigned upload URL using the committed speech ID
    upload_data = s3_service.get_upload_url(str(user.id), str(speech.id))
    speech.s3_url = upload_data['key']
    
    db.commit()
    db.refresh(speech)

    return UploadRequestResponse(
        interest=chosen_interest.name,
        topic=topic,
        user_id=str(user.id),
        upload_url=upload_data['upload_url'],
        upload_method=upload_data.get('method', 'PUT'),
        upload_fields=upload_data.get('fields'),
        video_path=upload_data['key']
    )

@router.get('/{target_user_id}/{video_id}/play-token', response_model=VideoReadResponse)
async def get_video_play_token(
    target_user_id: str,
    video_id: str,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session),
    s3_service: S3SecureService = Depends(get_s3_service)
):
    supertokens_user_id = session.get_user_id()

    user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    if str(user.id) != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )
    
    try:
        read_data = s3_service.get_read_url(target_user_id, video_id)
        return VideoReadResponse(
            user_id=target_user_id,
            video_path=read_data['key'],
            download_url=read_data['download_url']
        )
    except Exception as _:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Video not found or access error'
        )

@router.put('/{video_id}/visibility', status_code=status.HTTP_200_OK, response_model=None)
async def set_video_visibility(
    video_id: str,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
):
    supertokens_user_id = session.get_user_id()

    user: User | None = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    speech: Speech | None = db.query(Speech).filter(
        Speech.id == video_id,
        Speech.user_id == user.id
    ).first()

    if speech is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Speech not found'
        )
    
    if speech.visibility_level == SpeechVisibility.PRIVATE:
        speech.visibility_level = SpeechVisibility.FRIENDS
    else:
        speech.visibility_level = SpeechVisibility.PRIVATE
    db.commit()
    db.refresh(speech)

    return