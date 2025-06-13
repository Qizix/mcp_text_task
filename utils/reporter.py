"""
Markdown report generation for MCP competitor tracking.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import logging

from utils.ai_summarizer import generate_full_report

async def generate_markdown_report(changes_by_site, output_dir="reports", prefix="weekly_changes"):
    today = datetime.today().strftime("%Y-%m-%d")
    filename = prefix + "_" + today + ".md"
    output_path = Path(output_dir) / filename

    filtered_changes = []
    for site in changes_by_site:
        if site.get("new_changes") or site.get("pricing_changed"):
            filtered_changes.append(site)

    try:
        if len(filtered_changes) == 0:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("No changes.", encoding="utf-8")
            logging.info("Report saved to %s" % output_path)
            return

        report_text = await generate_full_report(filtered_changes)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding="utf-8")
        logging.info("Report saved to %s" % output_path)
    except Exception as e:
        logging.exception("Failed to generate or save markdown report: %s" % e)