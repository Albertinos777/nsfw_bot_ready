import requests
from bs4 import BeautifulSoup
import random

def fetch_nudegals(limit=10):
    print("[DEBUG] fetch_nudegals()")
    results = []
    try:
        for page in range(1, 4):
            url = f"https://www.nudegals.com/page/{page}/"
            r = requests.get(url)
            if not r.ok:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all("article")

            for post in articles:
                title = post.find("h2").text.strip()
                link = post.find("a")["href"]
                thumb = post.find("img")["src"]

                video_page = requests.get(link)
                if not video_page.ok:
                    continue

                video_soup = BeautifulSoup(video_page.text, "html.parser")
                video_tag = video_soup.find("video")
                if video_tag:
                    source = video_tag.find("source")
                    if source and source["src"].endswith(".mp4"):
                        results.append({
                            "title": title,
                            "link": source["src"],
                            "thumb": thumb,
                            "ext": "mp4"
                        })
                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break
    except Exception as e:
        print(f"[!] NudeGals error: {e}")

    return results
