import datetime
from main_common import post_to_note

today = datetime.datetime.now().strftime("%Y%m%d")
filename = f"output/weekly-ai-news-{today}.md"

with open(filename, "r", encoding="utf-8") as f:
    markdown = f.read()

post_to_note(markdown)
