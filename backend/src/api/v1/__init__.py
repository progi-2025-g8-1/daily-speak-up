from .health import router as health_router
from .user import router as user_router
from .topic import router as topic_router
from .userdata import router as userdata_router
from .onboarding import router as onboarding_router
from .handles import router as handles_router
from .interests import router as interests_router
from .video import router as video_router
from .photo import router as photo_router

__all__ = [
    'health_router',
    'user_router',
    'topic_router',
    'userdata_router',
    'onboarding_router',
    'handles_router',
    'interests_router',
    'video_router',
    'photo_router'
]
