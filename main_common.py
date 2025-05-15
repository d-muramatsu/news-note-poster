# main_common.py

import feedparser, re, os, yaml
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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

def remove_non_bmp(text):
    return re.sub(r'[\U00010000-\U0010FFFF]', '', text)

def post_to_note(markdown_text):
    NOTE_EMAIL = os.getenv("NOTE_EMAIL")
    NOTE_PASSWORD = os.getenv("NOTE_PASSWORD")

    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://note.com/login")
        time.sleep(3)

        driver.find_element(By.CSS_SELECTOR, "#email").send_keys(NOTE_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "#email").send_keys(Keys.RETURN)
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "#password").send_keys(NOTE_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "#password").send_keys(Keys.RETURN)
        time.sleep(5)

        driver.get("https://note.com/notes/new")
        time.sleep(5)

        title = f"きょうのAIニュースまとめ - {time.strftime('%Y/%m/%d')}"
        driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='記事タイトル']").send_keys(title)

        cleaned_text = remove_non_bmp(markdown_text)
        body_area = driver.find_element(By.CSS_SELECTOR, "div.ProseMirror")
        body_area.click()

        for line in cleaned_text.split("\n"):
            body_area.send_keys(line)
            body_area.send_keys(Keys.ENTER)

        time.sleep(2)
        driver.find_element(By.XPATH, "//span[contains(text(),'公開に進む')]").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//span[contains(text(),'投稿')]").click()
        time.sleep(3)
        print("noteに記事を公開したよ！！")

    except Exception as e:
        print(f"投稿時にエラー：{e}")
    finally:
        time.sleep(10)
        driver.quit()
