import json
from typing import List, Dict
import asyncio
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

class Tracker:
    CATEGORY_LABELS = [
        "Pricing Intelligence",
        "Feature Tracking",
        "Market Positioning"
    ]

    def __init__(self, name, base_url, config, model, classifier, threshold=0.8):
        self.name = name
        self.base_url = base_url
        self.config = config
        self.model = model
        self.classifier = classifier
        self.threshold = threshold

    async def track_pricing(self):
        url = self.base_url + self.config["pricing_page"]
        html = await fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        selector = self.config.get("price_selector")
        elements = soup.select(selector)
        return self.clean_text(elements)

    async def track_blogs(self):
        url = self.base_url + self.config["blog_page"]
        html = await fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        selector = self.config.get("blog_selector")
        elements = soup.select(selector)
        filtered = [
            e for e in elements
            if not any(y in e.get_text() for y in ["2021", "2022", "2023", "2024"])
        ]
        return self.clean_text(filtered)

    def clean_text(self, elements):
        return [line for element in elements for line in re.split(r"[\n•\-]+", element.get_text(strip=True)) if line.strip()]

    def embed(self, lines):
        return self.model.encode(lines, convert_to_tensor=True)

    def detect_new_lines(self, old_lines, new_lines):
        if not old_lines:
            return new_lines

        old_emb = self.embed(old_lines)
        new_emb = self.embed(new_lines)
        sim = util.pytorch_cos_sim(new_emb, old_emb)

        result = []
        for i, row in enumerate(new_lines):
            if sim[i].max().item() < self.threshold:
                result.append(row)
        return result

    async def classify(self, lines):
        grouped = defaultdict(list)
        for line in lines:
            result = self.classifier(line, candidate_labels=self.CATEGORY_LABELS)
            label = result["labels"][0]
            grouped[label].append(line)
        return dict(grouped)

    async def run(self, old_data):
        pricing = await self.track_pricing()
        blog = await self.track_blogs()
        combined = pricing + blog

        old_lines = old_data.get(self.name, [])
        new_lines = self.detect_new_lines(old_lines, combined)
        categorized = await self.classify(new_lines)

        return self.name, {
            "new_features": new_lines,
            "categorized": categorized,
            "all_lines": combined
        }