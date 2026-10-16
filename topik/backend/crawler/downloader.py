"""
Concurrent M3U8 video downloader.

Usage:
    asyncio.run(download_m3u8("https://example.com/video.m3u8", "output.mp4"))
"""

import asyncio
import re
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import aiofiles
import aiohttp


# ── configuration ────────────────────────────────────────────────────────────

DEFAULT_CONCURRENCY = 16  # simultaneous segment downloads              并发数量
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=1200, connect=10)           # 超时
# 伪装头
DEFAULT_HEADERS = {                                                         
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ── m3u8 parsing ─────────────────────────────────────────────────────────────

def _base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"


def _parse_segments(m3u8_text: str, base: str) -> list[str]:
    """Return absolute URLs for every .ts / media segment in the playlist."""
    segments: list[str] = []
    for line in m3u8_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        segments.append(line if line.startswith("http") else urljoin(base, line))
    return segments


def _pick_best_stream(m3u8_text: str, base: str) -> str | None:
    """If this is a master playlist, return the URL of the highest-bandwidth variant."""
    best_url: str | None = None
    best_bw = -1
    lines = m3u8_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF"):
            m = re.search(r"BANDWIDTH=(\d+)", line)
            bw = int(m.group(1)) if m else 0
            if bw > best_bw and i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                best_bw = bw
                best_url = candidate if candidate.startswith("http") else urljoin(base, candidate)
    return best_url


# ── download helpers ──────────────────────────────────────────────────────────

async def _fetch_text(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.text()


async def _download_segment(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    url: str,
    dest: Path,
    index: int,
) -> None:
    async with sem:
        for attempt in range(3):
            try:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.read()
                async with aiofiles.open(dest / f"{index:06d}.ts", "wb") as f:
                    await f.write(data)
                return
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(f"segment {index} failed after 3 attempts: {exc}") from exc
                await asyncio.sleep(1.5 ** attempt)


async def _merge_segments(segment_dir: Path, output_path: str, total: int) -> None:
    """Concatenate ordered .ts files into a single output file."""
    async with aiofiles.open(output_path, "wb") as out:
        for i in range(total):
            seg = segment_dir / f"{i:06d}.ts"
            async with aiofiles.open(seg, "rb") as f:
                await out.write(await f.read())


# ── public API ────────────────────────────────────────────────────────────────

async def download_m3u8(
    url: str,
    output: str,
    *,
    concurrency: int = DEFAULT_CONCURRENCY,
    headers: dict | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
    progress_cb=None,  # optional async callable(done: int, total: int)
) -> None:
    """
    Download a public M3U8 stream to *output* (any filename/path).

    Args:
        url:         M3U8 playlist URL (master or media).
        output:      Local destination file path (e.g. "video.mp4").
        concurrency: Max simultaneous segment downloads.
        headers:     Extra HTTP headers merged with defaults.
        timeout:     aiohttp timeout object.
        progress_cb: Optional async callback(done, total) for progress reporting.
    """
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    tmo = timeout or DEFAULT_TIMEOUT

    async with aiohttp.ClientSession(headers=hdrs, timeout=tmo) as session:
        # resolve master → media playlist if needed
        m3u8_text = await _fetch_text(session, url)
        base = _base_url(url)

        variant_url = _pick_best_stream(m3u8_text, base)
        if variant_url:
            url = variant_url
            m3u8_text = await _fetch_text(session, url)
            base = _base_url(url)

        segments = _parse_segments(m3u8_text, base)
        if not segments:
            raise ValueError("No media segments found in playlist.")

        total = len(segments)
        sem = asyncio.Semaphore(concurrency)
        done = 0

        with tempfile.TemporaryDirectory() as tmp:
            seg_dir = Path(tmp)

            async def _tracked(seg_url: str, idx: int) -> None:
                nonlocal done
                await _download_segment(session, sem, seg_url, seg_dir, idx)
                done += 1
                if progress_cb:
                    await progress_cb(done, total)
                else:
                    print(f"\r  {done}/{total} segments", end="", flush=True)

            await asyncio.gather(*[_tracked(s, i) for i, s in enumerate(segments)])
            print()  # newline after progress

            await _merge_segments(seg_dir, output, total)

    print(f"Saved → {output}")


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python downloader.py <m3u8_url> <output_file>")
        sys.exit(1)

    asyncio.run(download_m3u8(sys.argv[1], sys.argv[2]))
