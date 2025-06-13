"""
Main entry point for MCP competitor tracking.
Handles loading configs, running trackers, saving results, and generating reports.
"""

import asyncio
import json
import os
import logging
from datetime import datetime

from trackers.keyw_tracker import Tracker
from utils.changes_finder import extract_changes
from utils.reporter import generate_markdown_report
from utils.slack_reporter import send_report_to_slack

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/mcp.log"),
        logging.StreamHandler()
    ]
)

def load_configs_and_data():
    competitors = None
    try:
        with open("configs/competitors.json", encoding="utf-8") as f:
            competitors = json.load(f)
    except Exception as err:
        logging.error("Failed to load competitors config: %s" % err)
        raise

    old_data = {}
    try:
        with open("data/results.json", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                old_data = {entry["name"]: entry for entry in json.loads(content)}
    except FileNotFoundError:
        logging.warning("results.json not found, starting with empty old_data.")
    except Exception as e:
        logging.error("Failed to load results.json: %s" % e)
        raise

    return old_data, competitors

def save_data(new_results, changes):
    try:
        with open("data/results.json", "w", encoding="utf-8") as f:
            json.dump(new_results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error("Failed to save results.json: %s" % e)
        raise

    try:
        with open("data/diff.json", "w", encoding="utf-8") as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error("Failed to save diff.json: %s" % e)
        raise

async def main():
    try:
        old_data, competitors = load_configs_and_data()
        tasks = []
        for name, config in competitors.items():
            tracker = Tracker(config["name"], config)
            tasks.append(tracker.track_all())
        new_results = await asyncio.gather(*tasks)
        changes = extract_changes(old_data, new_results)
        save_data(new_results, changes)
        logging.info("Tracking complete. Changes saved to diff.json.")
        await generate_markdown_report(changes)
        logging.info("Weekly Markdown report saved to weekly_changes.md.")
        today = datetime.today().strftime("%Y-%m-%d")
        report_path = f"reports/weekly_changes_{today}.md"
        send_report_to_slack(report_path)
    except Exception as e:
        logging.exception("An error happened in main: %s" % e)

if __name__ == "__main__":
    asyncio.run(main())