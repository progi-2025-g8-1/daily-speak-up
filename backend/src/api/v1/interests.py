from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Interest

router = APIRouter(prefix="/interests", tags=["Interests"])

# Interest translations
INTEREST_TRANSLATIONS = {
    'en': {
        'technology': 'Technology',
        'sports': 'Sports',
        'music': 'Music',
        'movies': 'Movies',
        'books': 'Books',
        'travel': 'Travel',
        'food': 'Food',
        'art': 'Art',
        'gaming': 'Gaming',
        'fitness': 'Fitness',
        'science': 'Science',
        'fashion': 'Fashion',
        'photography': 'Photography',
        'nature': 'Nature',
        'politics': 'Politics'
    },
    'hr': {
        'technology': 'Tehnologija',
        'sports': 'Sport',
        'music': 'Glazba',
        'movies': 'Filmovi',
        'books': 'Knjige',
        'travel': 'Putovanja',
        'food': 'Hrana',
        'art': 'Umjetnost',
        'gaming': 'Igre',
        'fitness': 'Fitness',
        'science': 'Znanost',
        'fashion': 'Moda',
        'photography': 'Fotografija',
        'nature': 'Priroda',
        'politics': 'Politika'
    }
}


@router.get("")
async def get_interests(
    lang: str = Query("en", regex="^(en|hr)$"),
    db: Session = Depends(get_db)
):
    """Get all available interests with translations based on language parameter."""
    interests = db.query(Interest).all()
    
    result = []
    for interest in interests:
        # Get translation from INTEREST_TRANSLATIONS, fallback to English, then slug
        if lang in INTEREST_TRANSLATIONS and interest.slug in INTEREST_TRANSLATIONS[lang]:
            label = INTEREST_TRANSLATIONS[lang][interest.slug]
        elif 'en' in INTEREST_TRANSLATIONS and interest.slug in INTEREST_TRANSLATIONS['en']:
            label = INTEREST_TRANSLATIONS['en'][interest.slug]
        else:
            label = interest.name
        
        result.append({
            "slug": interest.slug,
            "label": label
        })
    
    return result
