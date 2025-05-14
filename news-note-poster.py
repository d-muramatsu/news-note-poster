# news-note-poster.py

import feedparser
import openai
from openai import OpenAI
import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv
import re
import yaml

load_dotenv()

# ====== 設定エリア ======
openai.api_key = os.getenv("OPENAI_API_KEY")
NOTE_EMAIL = os.getenv("NOTE_EMAIL")
NOTE_PASSWORD = os.getenv("NOTE_PASSWORD")
# =========================

def load_application_yaml(path="application.yaml"):
    with open(path, 'r', encoding='utf-8') as f:
        prompt_data = yaml.safe_load(f)
    return prompt_data

application_settings = load_application_yaml()

def fetch_ai_news():
    feed = feedparser.parse(application_settings["rss-url"])
    return feed.entries[:application_settings["max-articles"]]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_article(title, content):
    # テンプレ内の {title} や {content} を置換
    user_prompt = application_settings["user-prompt"].format(title=title, content=content)
    system_prompt = application_settings["system-prompt"]
    
    res = client.chat.completions.create(
        model=application_settings["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return res.choices[0].message.content.strip()

def generate_markdown(summaries):
    md = ""
    for i, item in enumerate(summaries):
        md += f"{item}\n\n"
        md += f"---\n\n"
    return md

def remove_non_bmp(text):
    # Unicodeの非BMP文字（絵文字など）を削除する正規表現
    return re.sub(r'[\U00010000-\U0010FFFF]', '', text)

def post_to_note(markdown_text):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # テスト中は画面見た方が安心！
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    try:
        # ログイン
        driver.get("https://note.com/login")
        time.sleep(3)

        driver.find_element(By.CSS_SELECTOR, "#email").send_keys(NOTE_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "#email").send_keys(Keys.RETURN)
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "#password").send_keys(NOTE_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "#password").send_keys(Keys.RETURN)
        time.sleep(5)

        # 新規作成ページへ
        driver.get("https://note.com/notes/new")
        time.sleep(5)

        # タイトル入力
        title = f"週刊AIニュースまとめ - {time.strftime('%Y/%m/%d')}"
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='記事タイトル']").send_keys(title)

        # 本文入力（非BMP除去）
        cleaned_text = remove_non_bmp(markdown_text)
        body_area = driver.find_element(By.CSS_SELECTOR, "div.ProseMirror")
        body_area.click()

        for line in cleaned_text.split("\n"):
            body_area.send_keys(line)
            # body_area.send_keys(Keys.SHIFT + Keys.ENTER)
            body_area.send_keys(Keys.ENTER)

        print("✅ 本文入力完了！")

        # ✅ 公開ボタンを押す処理（「公開に進む」）
        time.sleep(2)
        driver.find_element(By.XPATH, "//span[contains(text(),'公開に進む')]").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//span[contains(text(),'投稿する')]").click()
        time.sleep(3)
        print("🎉 投稿完了！！noteに公開されたよ！")

    except Exception as e:
        print(f"⚠️ 投稿時にエラー：{e}")

    finally:
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    news = fetch_ai_news()
    summaries = [summarize_article(n.title, n.summary) for n in news]
    markdown = generate_markdown(summaries)
    print(markdown)  # 念のため表示
    post_to_note(markdown)  # ← noteに投稿する！