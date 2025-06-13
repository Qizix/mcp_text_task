"""
AI summarizer utility for MCP competitor tracking.
"""

import aiohttp
import certifi
import ssl
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

headers = {
    "Content-Type": "application/json"
}

def load_prompt():
    try:
        with open("configs/prompt.json", encoding="utf-8") as f:
            data = json.load(f)
        return data["business_intel_prompt"]
    except Exception as e:
        logging.error(f"Failed to load prompt.json: {e}")
        return "{{input_text}}"

async def generate_full_report(company_changes):
    try:
        input_content = []
        for company in company_changes:
            name = company.get("name", "")
            all_texts = company.get("all_texts", [])
            urgent_lines = []
            normal_lines = []
            for item in all_texts:
                if item.get("urgent"):
                    urgent_lines.append("[URGENT] " + item.get("text", ""))
                else:
                    normal_lines.append(item.get("text", ""))
            pricing_text = company.get("pricing_text", [])
            pricing_changed = company.get("pricing_changed", False)
            old_pricing = company.get("old_pricing_text", [])

            section = name + ":\n"
            if urgent_lines:
                section += "\n".join(urgent_lines) + "\n"
            if normal_lines:
                section += "\n".join(normal_lines) + "\n"
            if pricing_changed:
                section += "\n[PRICING CHANGE]\nOld pricing:\n"
                section += "\n".join(old_pricing) + "\nNew pricing:\n"
                section += "\n".join(pricing_text) + "\n"
            else:
                section += "\n[PRICING]\n" + "\n".join(pricing_text) + "\n"
            input_content.append(section.strip())

        input_text = "\n\n".join(input_content)
        prompt_template = load_prompt()
        prompt = prompt_template.replace("{{input_text}}", input_text)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        if not API_KEY:
            logging.error("GOOGLE_API_KEY not set in environment.")
            return "Summary unavailable (no API key set in environment variable GOOGLE_API_KEY)."

        async with aiohttp.ClientSession() as session:
            async with session.post(
                ENDPOINT + "?key=" + API_KEY,
                headers=headers,
                json=payload,
                ssl=ssl_context
            ) as resp:
                result = await resp.json()
                if "candidates" in result:
                    try:
                        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    except Exception as e:
                        logging.error(f"Error parsing API response: {e}")
                        return "Summary unavailable."
                elif "error" in result:
                    logging.error(f"API error: {result['error'].get('message', 'Unknown error')}")
                    return "Summary unavailable (API error: " + result["error"].get("message", "Unknown error") + ")"
                else:
                    logging.error("Unknown API response structure.")
                    return "Summary unavailable."
    except Exception as e:
        logging.exception(f"Error generating full report: {e}")
        return "Summary unavailable."
    
    