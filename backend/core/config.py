
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    # Direct PostgreSQL access
    DATABASE_URL: str  # ✅ uppercase

    class Config:
        env_file = ".env"

settings = Settings()
