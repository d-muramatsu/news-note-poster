import datetime
import feedparser, os, yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def load_application_yaml(path="application.yaml"):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_ai_news(settings):
    feed = feedparser.parse(settings["rss-url"])
    return feed.entries[:settings["max-articles"]]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_article(settings, title, content):
    user_prompt = settings["user-prompt"].format(title=title, content=content)
    system_prompt = settings["system-prompt"]

    res = client.chat.completions.create(
        model=settings["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return res.choices[0].message.content.strip()

def generate_markdown(summaries):
    return "\n\n---\n\n".join(summaries) + "\n"

if __name__ == "__main__":
    application_settings = load_application_yaml()
    news = fetch_ai_news(application_settings)
    summaries = [summarize_article(application_settings, n.title, n.summary) for n in news]
    markdown = generate_markdown(summaries)

    # 日付を "YYYYMMDD" 形式で取得
    today = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"output/weekly-ai-news-{today}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Markdownファイルを生成しました → {filename}")
