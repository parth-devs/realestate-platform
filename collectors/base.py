import time
import random
from typing import Any, Dict, List
from loguru import logger
from config import settings

try:
    from curl_cffi import requests as cffi_requests
    USE_CURL_CFFI = True
except ImportError:
    import requests as cffi_requests
    USE_CURL_CFFI = False

class BaseCollector:
    def __init__(self, source_name: str):
        self.source_name = source_name
        if USE_CURL_CFFI:
            self.session = cffi_requests.Session(impersonate="chrome124")
        else:
            import requests
            self.session = requests.Session()

    def get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

    def sleep_polite(self):
        """Random delay to avoid rate limiting and IP bans"""
        delay = random.uniform(settings.DELAY_MIN, settings.DELAY_MAX)
        logger.debug(f"Polite delay: sleeping {delay:.2f} seconds...")
        time.sleep(delay)

    def fetch(self, url: str, params: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None):
        """Fetch URL using browser-fingerprint impersonation with retries"""
        req_headers = headers or self.get_headers()
        proxies = {"http": settings.PROXY_URL, "https": settings.PROXY_URL} if settings.PROXY_URL else None

        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                self.sleep_polite()
                response = self.session.get(
                    url,
                    params=params,
                    headers=req_headers,
                    proxies=proxies,
                    timeout=settings.REQUEST_TIMEOUT
                )
                if response.status_code == 200:
                    return response
                elif response.status_code in [403, 429]:
                    logger.warning(f"[{self.source_name}] Blocked (HTTP {response.status_code}) on {url}. Retrying ({attempt}/{settings.MAX_RETRIES})...")
                    time.sleep(2 ** attempt * 2)
                else:
                    logger.warning(f"[{self.source_name}] HTTP {response.status_code} for URL: {url}")
            except Exception as e:
                logger.error(f"[{self.source_name}] Network error on attempt {attempt}: {e}")
                time.sleep(2 ** attempt)

        logger.error(f"[{self.source_name}] Failed to fetch {url} after {settings.MAX_RETRIES} attempts.")
        return None

    def run(self, city_or_county: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("Each collector must implement the run() method.")
