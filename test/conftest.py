import sys
import os
import pytest
from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import supertokens_python
    from supertokens_python.framework import fastapi as st_fastapi
    from starlette.middleware.base import BaseHTTPMiddleware
    
    supertokens_python.get_all_cors_headers = lambda: []

    class MockMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    st_fastapi.get_middleware = lambda: MockMiddleware

    from backend.src.services import supertokens_service
    supertokens_service.init_supertokens = lambda: None

except ImportError as e:
    print(f'Warning: Could not mock supertokens_service: {e}')

try:
    from backend.src.main import app
except ImportError as e:
    raise ImportError(f'Could not import `backend.src.main`. Ensure requirements are installed and path is correct. Error: {e}')

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
