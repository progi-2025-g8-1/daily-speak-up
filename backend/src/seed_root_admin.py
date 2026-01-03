from supertokens_python.recipe.emailpassword.asyncio import sign_up
from supertokens_python.recipe.emailpassword.interfaces import SignUpOkResult, EmailAlreadyExistsError
from typing import Optional
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_root_admin(
    email: str,
    password: str,
    tenant_id: str = "public",
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Optional[str]:
    """
    Creates a root admin user.
    
    Args:
        email: Admin email address
        password: Admin password
        tenant_id: Tenant ID (default is "public")
        max_retries: Number of retries on connection errors
        retry_delay: Seconds to wait between retries
    
    Returns:
        User ID if successful, None if user already exists
    """
    
    for attempt in range(max_retries):
        try:
            return await _create_root_admin_impl(email, password, tenant_id)
        except Exception as e:
            error_msg = str(e)
            if ("disconnected" in error_msg.lower() or "No SuperTokens core available" in error_msg) and attempt < max_retries - 1:
                logger.warning(f"SuperTokens connection failed, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Error creating root admin: {e}")
                raise

async def _create_root_admin_impl(email: str, password: str, tenant_id: str) -> Optional[str]:
    """Internal implementation of root admin creation."""
    
    # Create the user account
    signup_result = await sign_up(
        tenant_id=tenant_id,
        email=email,
        password=password
    )
    
    if isinstance(signup_result, EmailAlreadyExistsError):
        from supertokens_python.asyncio import list_users_by_account_info
        from supertokens_python.types.base import AccountInfoInput

        logger.info(f"SuperTokens root admin with email {email} already exists")

        users = await list_users_by_account_info(tenant_id, AccountInfoInput(email=email))
        existing_user = users[0]

        # Try to insert root admin in DSU database if not already present
        insert_root_admin_into_db(email=email, user_supertokens_id=existing_user.id)
        return None
    
    if isinstance(signup_result, SignUpOkResult):
        user_id = signup_result.user.id
        logger.info(f"Created SuperTokens user account with ID: {user_id}")
        
        # Create root admin in DSU database
        insert_root_admin_into_db(email=email, user_supertokens_id=user_id)
        return user_id
    
    return None

def insert_root_admin_into_db(email: str, user_supertokens_id: str):
    """
    Insert root admin user into DSU database if not already present.
    Args:
        email: Admin email address
        user_supertokens_id: SuperTokens user ID
    """
    from sqlalchemy.orm import Session
    from .db import engine
    from .api.config import get_settings
    from .models import User
    from .models.enums import UserRole, OnboardingStatus

    settings = get_settings()

    with Session(engine) as db_session:
        user_exists = db_session.query(User).filter(User.email == email).first()

        if not user_exists:
            admin_user = User(
                supertokens_user_id=user_supertokens_id,
                email=email,
                handle=settings.ROOT_ADMIN_HANDLE,
                role=UserRole.ADMIN,
                onboarding_status=OnboardingStatus.COMPLETED
            )
            db_session.add(admin_user)
            db_session.commit()
            logger.info(f"Created DSU root admin user with email: {email}")
        else:
            logger.info(f"DSU root admin user with email {email} already exists")
            if user_exists.supertokens_user_id != user_supertokens_id:
                user_exists.supertokens_user_id = user_supertokens_id
                db_session.commit()
                logger.info(f"Updated DSU root admin user {email} with SuperTokens ID: {user_supertokens_id}")
            