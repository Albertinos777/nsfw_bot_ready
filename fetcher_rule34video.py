# fetcher_rule34video.py
import requests
from bs4 import BeautifulSoup

def fetch_rule34video(limit=10):
    print("[DEBUG] fetch_rule34video()")
    results = []
    try:
        base = "https://rule34video.com/latest-updates/"
        page = requests.get(base)
        soup = BeautifulSoup(page.content, "html.parser")
        cards = soup.select("div.video-thumb")[:limit]

        for div in cards:
            a = div.find("a")
            title = a["title"]
            href = a["href"]
            video_page = requests.get(href)
            video_soup = BeautifulSoup(video_page.content, "html.parser")
            source = video_soup.find("video").find("source")
            link = source["src"]
            results.append({
                "title": title,
                "link": link,
                "thumb": link,
                "ext": "mp4"
            })
    except Exception as e:
        print(f"[!] Errore Rule34Video: {e}")
    return results
