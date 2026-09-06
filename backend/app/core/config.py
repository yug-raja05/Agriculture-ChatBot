import os
from typing import List, Union
from pydantic import AnyHttpUrl, BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def parse_cors(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AgriGenius AI"
    
    # Security & Hashing
    SECRET_KEY: str = Field(default="super_secret_cryptographic_key_replace_in_production", validation_alias="SECRET_KEY")
    JWT_SECRET: str = Field(default="jwt_access_token_secret_signing_key_replace_in_production", validation_alias="JWT_SECRET")
    JWT_REFRESH_SECRET: str = Field(default="jwt_refresh_token_secret_signing_key_replace_in_production", validation_alias="JWT_REFRESH_SECRET")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = 60  # requests
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors)
    ] = Field(default=["*"], validation_alias="CORS_ORIGINS")
    
    # MongoDB Atlas Connection
    MONGODB_URI: str = Field(
        default="mongodb+srv://DashGenius:Harsh_1617@agrigeniusai.ccyydcn.mongodb.net/?appName=AgriGeniusAI",
        validation_alias="MONGODB_URI"
    )
    MONGODB_DB_NAME: str = "AgriGeniusAI"
    
    # Vector Store Configuration
    VECTOR_STORE_COLLECTION: str = "vector_store"
    
    # External Integration API Keys
    MISTRAL_API_KEY: str = Field(default="", validation_alias="MISTRAL_API_KEY")
    MISTRAL_MODEL: str = Field(default="mistral-small-latest", validation_alias="MISTRAL_MODEL")
    ACTIVE_WEATHER_PROVIDER: str = Field(default="openweather", validation_alias="ACTIVE_WEATHER_PROVIDER")
    ACTIVE_MARKET_PROVIDER: str = Field(default="government", validation_alias="ACTIVE_MARKET_PROVIDER")
    ACTIVE_GOVERNMENT_PROVIDER: str = Field(default="database", validation_alias="ACTIVE_GOVERNMENT_PROVIDER")
    ACTIVE_NOTIFICATION_PROVIDER: str = Field(default="email", validation_alias="ACTIVE_NOTIFICATION_PROVIDER")
    WEATHER_API_KEY: str = Field(default="placeholder_weather_key", validation_alias="WEATHER_API_KEY")
    MARKET_API_KEY: str = Field(default="placeholder_market_key", validation_alias="MARKET_API_KEY")
    GOOGLE_MAPS_API_KEY: str = Field(default="placeholder_maps_key", validation_alias="GOOGLE_MAPS_API_KEY")
    HF_TOKEN: str = Field(default="", validation_alias="HF_TOKEN")
    HUGGINGFACE_API_KEY: str = Field(default="", validation_alias="HUGGINGFACE_API_KEY")
    CHATBOT_API_KEY: str = Field(default="", validation_alias="CHATBOT_API_KEY")
    EMAIL_SERVICE_KEY: str = Field(default="placeholder_email_key", validation_alias="EMAIL_SERVICE_KEY")
    SMS_SERVICE_KEY: str = Field(default="placeholder_sms_key", validation_alias="SMS_SERVICE_KEY")
    
    # SMS (Twilio) Configuration
    TWILIO_ACCOUNT_SID: str = Field(default="", validation_alias="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", validation_alias="TWILIO_AUTH_TOKEN")
    TWILIO_NUMBER: str = Field(default="", validation_alias="TWILIO_NUMBER")
    
    # Push (FCM) Configuration
    FCM_SERVER_KEY: str = Field(default="", validation_alias="FCM_SERVER_KEY")
    
    # SMTP Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, validation_alias="SMTP_PORT")
    SMTP_USER: str = Field(default="your_email@gmail.com", validation_alias="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", validation_alias="SMTP_PASSWORD")
    
    # AI/ML Config Paths and Models
    QWEN_MODEL_PATH: str = Field(default="Qwen/Qwen2.5-7B-Instruct", validation_alias="QWEN_MODEL_PATH")
    EMBEDDING_MODEL: str = Field(default="intfloat/multilingual-e5-base", validation_alias="EMBEDDING_MODEL")
    WHISPER_MODEL: str = Field(default="openai/whisper-base", validation_alias="WHISPER_MODEL")
    COQUI_MODEL: str = Field(default="tts_models/multilingual/multi-dataset/xtts_v2", validation_alias="COQUI_MODEL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")

settings = Settings()
