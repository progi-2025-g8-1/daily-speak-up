from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Interest

router = APIRouter(prefix="/interests", tags=["Interests"])


@router.get("")
async def get_interests(
    db: Session = Depends(get_db)
):
    """Get all available interests."""
    interests = db.query(Interest).all()
    
    return [
        {
            "slug": interest.slug,
            "label": interest.name.replace("_", " ").title()
        }
        for interest in interests
    ]
