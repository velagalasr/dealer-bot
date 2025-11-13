import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Application settings from environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE") or "0.3")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS") or "1000")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT") or "30")
    
    # API Configuration
    API_KEY: str = os.getenv("API_KEY", "default-dev-key")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DOCUMENTS_PATH: Path = Path(os.getenv("DOCUMENTS_PATH", str(DATA_DIR / "documents")))
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(DATA_DIR / "vectors"))
    
    # Create directories if they don't exist
    DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    USE_REDIS: bool = os.getenv("USE_REDIS", "False").lower() == "true"
    
    # Application Configuration
    APP_NAME: str = "Dealer Bot"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    
    # LLM Configuration
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Vector Database Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configurations are set"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        return True

# Create settings instance
settings = Settings()