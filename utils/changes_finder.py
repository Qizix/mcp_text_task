"""
Change extraction utility for MCP competitor tracking.
"""

import logging


def extract_changes(old_data, new_results):
    changes = []
    for result in new_results:
        try:
            name = result["name"]
            all_texts = result.get("all_texts", [])
            pricing_text = result.get("pricing_text", [])

            old_entry = old_data.get(name, {})
            old_all_texts = old_entry.get("all_texts", [])
            old_pricing = old_entry.get("pricing_text", [])

            old_texts_set = set()
            for item in old_all_texts:
                if "text" in item:
                    old_texts_set.add(item["text"])
            new_topics = []
            for item in all_texts:
                if item.get("text") not in old_texts_set:
                    new_topics.append(item)
            pricing_changed = pricing_text != old_pricing

            entry = {
                "name": name,
                "all_texts": new_topics,
                "pricing_text": pricing_text,
            }
            if pricing_changed:
                entry["pricing_changed"] = True
                entry["old_pricing_text"] = old_pricing

            if new_topics or pricing_changed:
                changes.append(entry)
        except Exception as e:
            logging.error("Error extracting changes for result: %s. Error: %s" % (result, e))
    return changes