import os
import requests

def send_report_to_slack(report_path):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set in environment")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    max_length = 3500
    if len(report_content) > max_length:
        report_content = report_content[:max_length] + "\n...(truncated)..."

    payload = {
        "text": "Weekly MCP Report:\n" + report_content
    }

    resp = requests.post(webhook_url, json=payload)
    if resp.status_code != 200:
        print(f"Failed to send Slack notification: {resp.status_code} {resp.text}")
