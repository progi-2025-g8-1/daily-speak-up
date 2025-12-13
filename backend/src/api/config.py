import configparser
import os
from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

_settings: 'Settings | None' = None

# Load .env file from the backend directory (next to src/)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class Settings(BaseSettings):
    def __init__(self) -> None:
        super().__init__()
        self._config_parser = self._load_config_file()

    def _load_config_file(self) -> configparser.ConfigParser | None:
        """Load configuration from app.conf file"""
        ...

    def _get_config_value(self, section: str, key: str, default: str = '') -> str:
        """Get value from config file."""
        if self._config_parser and self._config_parser.has_option(section, key):
            return self._config_parser.get(section, key)
        return default
    
    # region properties
    
    @property
    def environment(self) -> str:
        return getenv('ENVIRONMENT', 'dev')
    
    @property
    def auth0_domain(self) -> str:
        return getenv('AUTH0_DOMAIN', '')
    
    @property
    def auth0_api_audience(self) -> str:
        return getenv('AUTH0_AUDIENCE', 'http://localhost:8123/')
    
    @property
    def auth0_algorithms(self) -> str:
        return getenv('AUTH0_ALGORITHMS', 'RS256')
    
    @property
    def auth0_issuer(self) -> str:
        return f'https://{self.auth0_domain}/'
    
    @property
    def gemini_api_key(self) -> str:
        """Get Gemini API key from environment."""
        key = getenv('GEMINI_API_KEY', '')
        if not key:
            raise ValueError('GEMINI_API_KEY is not set in environment variables')
        return key
    
    @property
    def gemini_model_id(self) -> str:
        """Get Gemini model ID from environment."""
        return getenv('GEMINI_MODEL_ID', 'gemini-2.0-flash-exp')
    
    @property
    def CELERY_BROKER_URL(self) -> str:
        return getenv('RABBIT_MQ_URL', 'amqp://guest:guest@rabbitmq:5672/')

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return getenv('CELERY_RESULT_BACKEND', 'rpc://')
        
    @property
    def RESEND_API_KEY(self) -> str:
        """Get Resend API key from environment."""
        key = getenv('RESEND_API_KEY', '')
        if not key:
            raise ValueError('RESEND_API_KEY is not set in environment variables')
        return key

    @property
    def RESEND_FROM_EMAIL(self) -> str:
        return getenv('RESEND_FROM_EMAIL', 'noreply@dailyspeak.app')
    
    @property
    def CELERY_RATE_LIMIT(self) -> str:
        return getenv('CELERY_RATE_LIMIT', '2/s')
    
    # SuperTokens configuration
    @property
    def supertokens_connection_uri(self) -> str:
        """SuperTokens Core connection URI"""
        return getenv('SUPERTOKENS_CONNECTION_URI', 'http://localhost:3567')
    
    @property
    def supertokens_api_key(self) -> str:
        """SuperTokens API key for managed service (optional)"""
        return getenv('SUPERTOKENS_API_KEY', '')
    
    @property
    def app_name(self) -> str:
        return getenv('APP_NAME', 'DailySpeakUp')
    
    @property
    def api_domain(self) -> str:
        return getenv('API_DOMAIN', 'http://localhost:8123')
    
    @property
    def website_domain(self) -> str:
        return getenv('WEBSITE_DOMAIN', 'http://localhost:5173')
    
    @property
    def api_base_path(self) -> str:
        return getenv('API_BASE_PATH', '/auth')
    
    @property
    def google_client_id(self) -> str:
        """Google OAuth client ID"""
        return getenv('GOOGLE_CLIENT_ID', '')
    
    @property
    def google_client_secret(self) -> str:
        """Google OAuth client secret"""
        return getenv('GOOGLE_CLIENT_SECRET', '')
    
    @property
    def bucket_name(self) -> str:
        return getenv('BUCKET_NAME', '')
    
    @property
    def r2_account_id(self) -> str:
        return getenv('R2_ACCOUNT_ID', '')
    
    @property
    def r2_admin_api_token(self) -> str:
        return getenv('R2_ADMIN_API_KEY', '')
    
    @property
    def r2_access_key_id(self) -> str:
        return getenv('R2_ACCESS_KEY_ID', '')
    
    # endregion
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        extra = 'ignore'

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
