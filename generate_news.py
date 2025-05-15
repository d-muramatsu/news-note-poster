import datetime
from main_common import load_application_yaml, fetch_ai_news, summarize_article, generate_markdown

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
