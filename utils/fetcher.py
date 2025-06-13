"""
Async HTML fetcher utility for MCP competitor tracking.
"""

import asyncio
import aiohttp
import certifi
import ssl
import logging

async def fetch_html(url):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, ssl=ssl_context) as response:
                html = await response.text()
                return html
    except Exception as e:
        logging.error(f"Failed to fetch HTML from {url}: {e}")
        return ""
