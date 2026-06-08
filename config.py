"""
Configuration module for Answer Evaluation System.
All settings are loaded from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = Field(default="Subjective Answer Evaluator API", env="APP_NAME")
    APP_VERSION: str = Field(default="3.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(default="", env="SECRET_KEY")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", env="ALLOWED_ORIGINS")
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # seconds
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field(default=".pdf,.txt,.png,.jpg,.jpeg", env="ALLOWED_EXTENSIONS")
    
    # Models
    DEFAULT_MODEL: str = Field(default="MiniLM", env="DEFAULT_MODEL")
    SENTENCE_TRANSFORMER_MODELS: str = Field(
        default="all-MiniLM-L6-v2,all-mpnet-base-v2", 
        env="SENTENCE_TRANSFORMER_MODELS"
    )
    CNN_MODEL_PATH: str = Field(default="cnn_answer_evaluator.h5", env="CNN_MODEL_PATH")
    TOKENIZER_PATH: str = Field(default="tokenizer.pkl", env="TOKENIZER_PATH")
    
    # Scoring Weights (must sum to 1.0)
    WEIGHT_SIMILARITY: float = Field(default=0.40, env="WEIGHT_SIMILARITY")
    WEIGHT_COVERAGE: float = Field(default=0.25, env="WEIGHT_COVERAGE")
    WEIGHT_GRAMMAR: float = Field(default=0.15, env="WEIGHT_GRAMMAR")
    WEIGHT_RELEVANCE: float = Field(default=0.20, env="WEIGHT_RELEVANCE")
    
    # CNN Settings
    USE_CNN_BY_DEFAULT: bool = Field(default=False, env="USE_CNN_BY_DEFAULT")
    CNN_WEIGHT: float = Field(default=0.30, env="CNN_WEIGHT")  # Weight for CNN in hybrid scoring
    
    # OCR Settings
    OCR_MIN_TEXT_LENGTH: int = Field(default=100, env="OCR_MIN_TEXT_LENGTH")
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.6, env="OCR_CONFIDENCE_THRESHOLD")
    
    # LLM Settings (Google Gemini)
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-exp", env="GEMINI_MODEL")
    USE_LLM_FOR_REFERENCE: bool = Field(default=True, env="USE_LLM_FOR_REFERENCE")
    LLM_MAX_TOKENS: int = Field(default=500, env="LLM_MAX_TOKENS")
    LLM_TEMPERATURE: float = Field(default=0.3, env="LLM_TEMPERATURE")  # Lower for more focused answers
    
    # Database
    DATABASE_URL: Optional[str] = Field(default="sqlite:///./evaluations.db", env="DATABASE_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse ALLOWED_EXTENSIONS into a list."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]
    
    @property
    def sentence_transformer_models_list(self) -> List[str]:
        """Parse SENTENCE_TRANSFORMER_MODELS into a list."""
        return [model.strip() for model in self.SENTENCE_TRANSFORMER_MODELS.split(",") if model.strip()]
    
    @property
    def scoring_weights_valid(self) -> bool:
        """Check if scoring weights sum to approximately 1.0."""
        total = self.WEIGHT_SIMILARITY + self.WEIGHT_COVERAGE + self.WEIGHT_GRAMMAR + self.WEIGHT_RELEVANCE
        return abs(total - 1.0) < 0.001


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    if not settings.scoring_weights_valid:
        import warnings
        warnings.warn(
            f"Scoring weights do not sum to 1.0. Current sum: "
            f"{settings.WEIGHT_SIMILARITY + settings.WEIGHT_COVERAGE + settings.WEIGHT_GRAMMAR + settings.WEIGHT_RELEVANCE}"
        )
    if not settings.SECRET_KEY:
        import warnings
        warnings.warn(
            "SECRET_KEY is not set. Please configure a strong secret key in your .env file.",
            stacklevel=2
        )
    return settings
