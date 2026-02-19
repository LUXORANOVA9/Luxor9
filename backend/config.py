import os

class Settings:
    # Database (Neon PostgreSQL free tier)
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # App
    WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/data/workspaces")
    MAX_AGENT_TURNS = int(os.getenv("MAX_AGENT_TURNS", "80"))
    MAX_SANDBOXES = int(os.getenv("MAX_SANDBOXES", "3"))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Redis (Upstash free tier)
    UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL", "")
    UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN", "")

settings = Settings()
