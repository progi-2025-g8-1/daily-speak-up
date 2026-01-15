from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from supertokens_python.recipe.session import SessionContainer

from ..services import (
    AuthService,
    EmailService,
    GeminiService,
    CloudflareR2Service,
)
from ..services.auth_service import get_session
from ..services.email_impl.sender import ResendEmailSender
from ..db import get_db
from ..models import User
from .config import get_settings

_auth_service: AuthService | None = None
_email_service: EmailService | None = None
_gemini_service: GeminiService | None = None
_s3_service: CloudflareR2Service | None = None
_resend_email_sender: ResendEmailSender | None = None

def get_auth_service() -> AuthService:
    """Returns a preconfigured AuthService object"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

def get_email_service() -> EmailService:
    """Returns a preconfigured EmailService object"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def get_gemini_service() -> GeminiService:
    """Returns a preconfigured GeminiService object"""
    global _gemini_service
    if _gemini_service is None:
        settings = get_settings()
        _gemini_service = GeminiService(
            api_key=settings.gemini_api_key,
            model_id=settings.gemini_model_id
        )
    return _gemini_service

def get_s3_service() -> CloudflareR2Service:
    """Returns a preconfigured S3Service object"""
    global _s3_service
    if _s3_service is None:
        settings = get_settings()
        _s3_service = CloudflareR2Service(
            bucket_name=settings.bucket_name,
            account_id=settings.r2_account_id,
            admin_api_token=settings.r2_admin_api_token,
            r2_access_key_id=settings.r2_access_key_id,
            jurisdiction=settings.r2_jurisdiction
        )
    return _s3_service

def get_resend_email_sender() -> ResendEmailSender:
    """Returns a preconfigured Resend ResendEmailSender object"""
    global _resend_email_sender
    if _resend_email_sender is None:
        settings = get_settings()
        _resend_email_sender = ResendEmailSender(
            resend_api_key=settings.RESEND_API_KEY,
            from_email=settings.RESEND_FROM_EMAIL
        )
    return _resend_email_sender

async def get_current_user(
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(get_session)
) -> User:
    supertokens_user_id = session.get_user_id()
    
    user = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user