import time
import asyncio
import httpx
from .config import GITHUB_TOKENS

class TokenRotator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self._lock = asyncio.Lock()

    def get_headers(self, is_graphql=False):
        token = self.tokens[self.current_index]
        if is_graphql:
            return {"Authorization": f"Bearer {token}"}
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    async def rotate(self):
        async with self._lock:
            self.current_index = (self.current_index + 1) % len(self.tokens)
            msg = f"🔄 ROTATION: Switched to Token #{self.current_index + 1} due to rate limit."
            print(msg)
            from .load import log_message
            log_message(msg)

rotator = TokenRotator(GITHUB_TOKENS)

_client = None

def get_client():
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=30,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            http2=True
        )
    return _client

async def request_async(method, url, is_graphql=False, **kwargs):
    from .load import log_message
    max_retries = 3
    for attempt in range(max_retries):
        headers = rotator.get_headers(is_graphql)
        try:
            client = get_client()
            resp = await client.request(method, url, headers=headers, **kwargs)
        except Exception as e:
            print(f"⚠️ Network error: {e}. Retrying...")
            await asyncio.sleep(5)
            continue
        if resp.status_code == 200:
            return resp
        if resp.status_code in (403, 429):
            if len(GITHUB_TOKENS) > 1:
                await rotator.rotate()
                await asyncio.sleep(0.5)
                continue
            else:
                reset = resp.headers.get("X-RateLimit-Reset")
                wait = max(60, int(reset) - int(time.time()) + 5) if reset else 60
                msg = f"🛑 Rate limit — sleeping {wait}s..."
                print(msg)
                log_message(msg)
                await asyncio.sleep(wait)
                continue
        error_msg = f"❌ Server Error {resp.status_code}: {resp.text[:80]}"
        print(error_msg)
        log_message(error_msg)
        await asyncio.sleep(5)
    print("🚨 Max retries reached. Skipping.")
    return None

def request_with_retry(method, url, is_graphql=False, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        request_async(method, url, is_graphql=is_graphql, **kwargs)
    )

async def close_client():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
