import os
from typing import List

class DeploymentConfig:
    """Configuration for deployment"""
    
    # API Configuration - handle cloud deployment PORT variable
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    # Many cloud providers use PORT environment variable
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./alo_veda.db")
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", f"http://localhost:{int(os.getenv('FRONTEND_PORT', '8501'))}")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Production settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Cloud deployment detection
    IS_CLOUD_DEPLOYMENT: bool = any([
        os.getenv("RENDER"),
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("HEROKU_APP_NAME"),
        os.getenv("VERCEL"),
        os.getenv("NETLIFY")
    ])
    
    # Get the base URL for API calls
    @property
    def API_BASE_URL(self) -> str:
        if self.IS_CLOUD_DEPLOYMENT:
            # For cloud deployments, use the same domain
            return f"http://localhost:{self.API_PORT}"
        else:
            return f"http://localhost:{self.API_PORT}"

# Create a global config instance
config = DeploymentConfig() 