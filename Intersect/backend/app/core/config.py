import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend directory
PROJECT_ROOT = BASE_DIR.parent if (BASE_DIR.parent / "challenges").exists() else BASE_DIR

DEFAULT_DB_FILE = (PROJECT_ROOT / "ctf.db").resolve()
DEFAULT_CHALLENGES_DIR = (PROJECT_ROOT / "challenges").resolve()


class Settings:
    # --- General ---
    PROJECT_NAME: str = "CTF Platform"
    SECRET_KEY: str = os.environ.get("CTF_SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: timedelta = timedelta(hours=12)

    # --- Database ---
    DATABASE_URL: str = os.environ.get("CTF_DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE.as_posix()}")

    # --- Orchestration ---
    # "docker" for local/dev single-host Docker daemon, or "process" / "mock" for fallback.
    ORCHESTRATOR_BACKEND: str = os.environ.get("CTF_ORCHESTRATOR", "docker")
    CHALLENGE_NETWORK: str = os.environ.get("CTF_CHALLENGE_NETWORK", "ctf_challenge_net")
    CHALLENGE_HOST: str = os.environ.get("CTF_CHALLENGE_HOST", os.environ.get("CTF_HOST", "localhost"))
    INSTANCE_TTL_SECONDS: int = int(os.environ.get("CTF_INSTANCE_TTL", 60 * 45))  # 45 min default
    MAX_INSTANCES_PER_USER: int = int(os.environ.get("CTF_MAX_INSTANCES_PER_USER", 3))
    CLEANUP_INTERVAL_SECONDS: int = int(os.environ.get("CTF_CLEANUP_INTERVAL", 30))
    PORT_RANGE_START: int = int(os.environ.get("CTF_PORT_START", 30000))
    PORT_RANGE_END: int = int(os.environ.get("CTF_PORT_END", 40000))

    # --- Security & Rate Limiting ---
    RATE_LIMIT_SUBMISSIONS_PER_MINUTE: int = int(os.environ.get("CTF_RATE_LIMIT_SUBMISSIONS", 15))

    # --- Challenge registry ---
    CHALLENGES_DIR: str = os.environ.get("CTF_CHALLENGES_DIR", str(DEFAULT_CHALLENGES_DIR))


settings = Settings()


