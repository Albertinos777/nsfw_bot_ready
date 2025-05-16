import requests
from bs4 import BeautifulSoup
import random

def fetch_hqpornero(limit=10):
    print("[DEBUG] fetch_hqpornero()")
    results = []
    base_url = "https://hqpornero.com"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        main = requests.get(base_url + "/videos", headers=headers, timeout=10)
        soup = BeautifulSoup(main.content, "html.parser")

        video_links = [a['href'] for a in soup.select("a.video-thumb") if a['href'].startswith("/video/")]
        random.shuffle(video_links)

        for link in video_links:
            video_page = requests.get(base_url + link, headers=headers, timeout=10)
            if video_page.status_code != 200:
                continue

            vsoup = BeautifulSoup(video_page.content, "html.parser")
            title = vsoup.select_one("h1.entry-title")
            video_tag = vsoup.find("video")

            if not video_tag or not video_tag.find("source"):
                continue

            video_url = video_tag.find("source")['src']
            if not video_url.endswith(".mp4"):
                continue

            results.append({
                "title": title.text.strip() if title else "HQPornero",
                "link": video_url,
                "thumb": video_url,  # fallback
                "ext": "mp4"
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] HQPornero fetch error: {e}")

    return results
