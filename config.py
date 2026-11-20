import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "realestate_texas")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Targeting Scope: 'NATIONWIDE', 'METROS', or 'CUSTOM'
    TARGET_SCOPE: str = os.getenv("TARGET_SCOPE", "METROS")
    TARGET_STATE: str = os.getenv("TARGET_STATE", "ALL")

    # Anti-bot and delay settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 15))
    DELAY_MIN: float = float(os.getenv("DELAY_MIN_SECONDS", 1.5))
    DELAY_MAX: float = float(os.getenv("DELAY_MAX_SECONDS", 3.5))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))

    # Optional proxy pool
    PROXY_URL: str | None = os.getenv("PROXY_URL", None)

    def get_target_markets(self) -> list[dict]:
        """Loads list of targets based on TARGET_SCOPE"""
        metros_file = BASE_DIR / "data" / "us_states_and_metros.json"
        if metros_file.exists():
            try:
                data = json.loads(metros_file.read_text(encoding="utf-8"))
                if self.TARGET_SCOPE == "NATIONWIDE" or self.TARGET_SCOPE == "METROS":
                    return data.get("top_us_metros", [])
            except Exception:
                pass
        # Fallback default
        return [
            {"city": "Austin", "state": "TX"},
            {"city": "Dallas", "state": "TX"},
            {"city": "Houston", "state": "TX"},
            {"city": "Miami", "state": "FL"},
            {"city": "Atlanta", "state": "GA"},
            {"city": "New York", "state": "NY"},
            {"city": "Los Angeles", "state": "CA"}
        ]

settings = Settings()
