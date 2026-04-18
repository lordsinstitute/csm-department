"""
VulnScan shared async HTTP client.
Provides a pre-configured httpx.AsyncClient with safe defaults for passive scanning.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx

# Default headers that mimic a real browser to get accurate server responses
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Hard limits so a slow/unresponsive target doesn't stall the whole scan
_TIMEOUT = httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=5.0)

# Never follow more than 5 redirects (enough for real sites, avoids redirect loops)
_MAX_REDIRECTS = 5


@asynccontextmanager
async def build_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Async context manager returning a shared httpx.AsyncClient suitable for
    passive vulnerability scanning.

    Usage::

        async with build_client() as client:
            resp = await client.get("https://example.com")

    The client is closed automatically on exit.
    """
    async with httpx.AsyncClient(
        headers=_DEFAULT_HEADERS,
        timeout=_TIMEOUT,
        follow_redirects=True,
        max_redirects=_MAX_REDIRECTS,
        verify=False,          # We intentionally check TLS ourselves in ssl_tls module
        http2=True,            # Use HTTP/2 when available
    ) as client:
        yield client