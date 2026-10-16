"""
M3U8 URL fetcher using Playwright.

Launches a headless browser, navigates to a video page,
and intercepts network requests to capture M3U8 playlist URLs.

Usage:
    urls = asyncio.run(fetch_m3u8_urls("https://example.com/video"))
"""

import asyncio
import re

from playwright.async_api import async_playwright, Request

# 匹配 m3u8 的正则，兼容带 query string 的情况
_M3U8_PATTERN = re.compile(r"https?://[^\s\"']+\.m3u8[^\s\"']*", re.IGNORECASE)

# 等待页面加载期间监听请求的最长时间（秒）
DEFAULT_WAIT = 15


async def fetch_m3u8_urls(
    page_url: str,
    *,
    wait: int = DEFAULT_WAIT,
    headless: bool = True,
) -> list[str]:
    """
    Navigate to *page_url* and return all M3U8 URLs intercepted from network requests.

    Args:
        page_url: The video page URL to visit.
        wait:     Seconds to wait for M3U8 requests after page load.
        headless: Run browser in headless mode (set False to debug visually).

    Returns:
        Deduplicated list of M3U8 URLs found, in order of first appearance.
    """
    found: list[str] = []
    seen: set[str] = set()

    def _on_request(request: Request) -> None:
        url = request.url
        if _M3U8_PATTERN.search(url) and url not in seen:
            seen.add(url)
            found.append(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            # 忽略 HTTPS 证书错误
            ignore_https_errors=True,
        )
        page = await context.new_page()

        # 拦截所有网络请求
        page.on("request", _on_request)

        await page.goto(page_url, wait_until="domcontentloaded")

        # 等待视频播放器触发 m3u8 请求
        await asyncio.sleep(wait)

        await browser.close()

    return found


async def fetch_first_m3u8(page_url: str, **kwargs) -> str | None:
    """Convenience wrapper — returns only the first M3U8 URL found, or None."""
    urls = await fetch_m3u8_urls(page_url, **kwargs)
    return urls[0] if urls else None


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch.py <page_url>")
        sys.exit(1)

    results = asyncio.run(fetch_m3u8_urls(sys.argv[1]))
    if results:
        for url in results:
            print(url)
    else:
        print("No M3U8 URLs found.")
