"""
Competitor tracker implementation for MCP protocol.
"""

import json
import logging
from bs4 import BeautifulSoup

from utils.fetcher import fetch_html

class Tracker:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.urls = config.get("urls", {})
        self.block_classes = config.get("block_clasess", {})
        self.tracking_keywords = {}
        for page, kws in config.get("tracking_keywords", {}).items():
            self.tracking_keywords[page] = [kw.lower() for kw in kws]

    async def fetch_and_extract(self, page_key, selector_key, exclude_years=True):
        url = self.urls.get(page_key, "")
        if not url:
            logging.warning(f"No URL found for page_key: {page_key}")
            return []
        try:
            html = await fetch_html(url)
            if not html:
                logging.warning(f"No HTML fetched for {url}")
                return []
            soup = BeautifulSoup(html, "html.parser")
            selector = self.block_classes.get(selector_key, "")
            elements = soup.select(selector)

            texts = []
            for el in elements:
                text = el.get_text(separator=" ", strip=True)
                if exclude_years and any(y in text for y in ["2021", "2022", "2023", "2024"]):
                    continue
                texts.append(text)
            return texts
        except Exception as e:
            logging.error(f"Error fetching or extracting for {url}: {e}")
            return []

    def mark_urgent(self, lines, page_key):
        keywords = self.tracking_keywords.get(page_key, [])
        marked = []
        for line in lines:
            is_urgent = False
            for kw in keywords:
                if kw in line.lower():
                    is_urgent = True
                    break
            marked.append({"text": line, "urgent": is_urgent})
        return marked

    async def track_all(self):
        all_texts = []
        pricing_text = []

        for key in self.urls:
            try:
                page_text = await self.fetch_and_extract(key, key)
                if key == "pricing":
                    pricing_text = page_text
                else:
                    marked = self.mark_urgent(page_text, key)
                    all_texts.extend(marked)
            except Exception as e:
                logging.error(f"Error tracking {key} for {self.name}: {e}")

        return {
            "name": self.name,
            "all_texts": all_texts,
            "pricing_text": pricing_text
        }