import time
import asyncio
import httpx
import threading
from .config import GITHUB_TOKENS

class TokenRotator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self._lock = threading.Lock()

    def get_headers(self, is_graphql=False):
        token = self.tokens[self.current_index]
        if is_graphql:
            return {"Authorization": f"Bearer {token}"}
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    def rotate(self):
        with self._lock:
            self.current_index = (self.current_index + 1) % len(self.tokens)
            msg = f"🔄 ROTATION: Switched to Token #{self.current_index + 1}"
            print(msg)

rotator = TokenRotator(GITHUB_TOKENS)

def request_with_retry(method, url, is_graphql=False, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        headers = rotator.get_headers(is_graphql)
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.request(method, url, headers=headers, **kwargs)
        except Exception as e:
            print(f"⚠️ Network error: {e}. Retrying...")
            time.sleep(5)
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code in (403, 429):
            if len(GITHUB_TOKENS) > 1:
                rotator.rotate()
                time.sleep(1)
                continue
            else:
                reset = resp.headers.get("X-RateLimit-Reset")
                wait = max(60, int(reset) - int(time.time()) + 5) if reset else 60
                print(f"🛑 Rate limit — sleeping {wait}s...")
                time.sleep(wait)
                continue

        print(f"❌ Server Error {resp.status_code}: {resp.text[:80]}")
        time.sleep(5)

    print("🚨 Max retries reached. Skipping.")
    return None

async def request_async(method, url, is_graphql=False, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        headers = rotator.get_headers(is_graphql)
        try:
            async with httpx.AsyncClient(timeout=30, http2=True) as client:
                resp = await client.request(method, url, headers=headers, **kwargs)
        except Exception as e:
            print(f"⚠️ Network error: {e}. Retrying...")
            await asyncio.sleep(5)
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code in (403, 429):
            if len(GITHUB_TOKENS) > 1:
                rotator.rotate()
                await asyncio.sleep(1)
                continue
            else:
                reset = resp.headers.get("X-RateLimit-Reset")
                wait = max(60, int(reset) - int(time.time()) + 5) if reset else 60
                print(f"🛑 Rate limit — sleeping {wait}s...")
                await asyncio.sleep(wait)
                continue

        print(f"❌ Server Error {resp.status_code}: {resp.text[:80]}")
        await asyncio.sleep(5)

    print("🚨 Max retries reached. Skipping.")
    return None
