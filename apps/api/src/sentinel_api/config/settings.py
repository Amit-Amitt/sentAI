from typing import Literal, Optional, List
import structlog
from pydantic import field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sentinel_api.config.utils import mask_secret

logger = structlog.get_logger("sentinel_api.config")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="SENTINEL_",
    )

    # --- GENERAL ---
    APP_ENV: Literal["development", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] | str = ["http://localhost:3000", "http://localhost:3001"]

    # --- DATABASE ---
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_SSL_MODE: str = "prefer"

    # --- REDIS & QUEUE ---
    REDIS_URL: str
    QUEUE_CONCURRENCY: int = 5
    QUEUE_RETRY_COUNT: int = 3

    # --- AUTHENTICATION ---
    JWT_SECRET: str
    JWT_EXPIRES_IN: int = 3600
    AUTH_ENCRYPTION_KEY: str

    # --- FEATURE FLAGS ---
    ENABLE_AI: bool = True
    ENABLE_GITHUB: bool = True
    ENABLE_OTEL: bool = True
    ENABLE_KUBERNETES: bool = True
    ENABLE_PROMETHEUS: bool = True
    ENABLE_AUTO_REMEDIATION: bool = True
    ENABLE_NOTIFICATIONS: bool = True

    # --- AI PROVIDERS ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # --- VECTOR DATABASE ---
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # --- GITHUB INTELLIGENCE ---
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_PRIVATE_KEY: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None

    # --- KUBERNETES RUNTIME ---
    K8S_IN_CLUSTER: bool = False
    K8S_KUBECONFIG_PATH: str = "~/.kube/config"

    # --- OBSERVABILITY INTEGRATIONS ---
    PROMETHEUS_URL: Optional[str] = None
    GRAFANA_URL: Optional[str] = None
    GRAFANA_API_KEY: Optional[str] = None
    LOKI_URL: Optional[str] = None
    TEMPO_URL: Optional[str] = None
    ALERTMANAGER_URL: Optional[str] = None

    # --- STORAGE & NOTIFICATIONS ---
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None

    # --- SSO / IDENTITY PROVIDERS ---
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    SAML_IDP_URL: Optional[str] = None

    # --- BILLING & STRIPE ---
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    STRIPE_PRICE_FREE: Optional[str] = None
    STRIPE_PRICE_STARTER: Optional[str] = None
    STRIPE_PRICE_PRO: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE: Optional[str] = None
    
    DEFAULT_CURRENCY: str = "usd"


    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def parse_database_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v
        
    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_test(self) -> bool:
        return self.APP_ENV == "testing"


def validate_settings() -> Settings:
    """Initialize and eagerly validate settings, returning a helpful error message if required variables are missing."""
    try:
        cfg = Settings()
        return cfg
    except ValueError as e:
        # Pydantic's ValidationError contains a clear list of missing required fields.
        logger.error("APPLICATION STARTUP FAILED: Missing or Invalid Configuration.")
        print("\n--- CONFIGURATION ERROR ---")
        print("Sentinel AI could not start because the following required environment variables are missing or invalid:")
        
        from pydantic import ValidationError
        if isinstance(e, ValidationError):
            for err in e.errors():
                loc = ".".join([str(l) for l in err["loc"]])
                msg = err["msg"]
                print(f"  ❌ SENTINEL_{loc.upper()}: {msg}")
                
        print("\nPlease check your .env file or environment exports. See `.env.example` for a full list of configuration options.")
        print("---------------------------\n")
        
        # Stop application startup by re-raising
        raise RuntimeError("Missing required configuration") from e

# Eager evaluation on module load
settings = validate_settings()
BlockSettings = Settings
