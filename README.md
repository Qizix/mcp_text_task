MCP Competitor Tracking Project

This project tracks competitors' websites for changes and generates reports.

How to run:

1. Make sure you have Python 3.9+ installed.
2. Install requirements. You can do this with:
   pip install -r requirements.txt

3. Set up your environment variables. You need a .env file with GOOGLE_API_KEY for the AI summarizer.

.env file example:
GOOGLE_API_KEY=your_google_api_key_here

The GOOGLE_API_KEY is needed for the AI summarizer to work. You can obtain it from the Google Playground for free.

4. Prepare the configs:
   - configs/competitors.json should have the competitors and their settings.
   - configs/prompt.json should have the prompt for the AI summarizer.

5. To start tracking, just run:
   python main.py

6. The script will fetch data, compare with previous results, and save changes.
   - Results are saved in data/results.json and data/diff.json
   - A markdown report is generated in the reports/ folder.

If you have any errors, check mcp.log for details.

That's it.
