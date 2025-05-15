import requests
from bs4 import BeautifulSoup
import random

def fetch_pornhub(limit=10):
    print("[+] Fetching from Pornhub...")
    results = []
    try:
        tags = ["creampie", "facial", "cosplay", "cumshot", "amateur"]
        tag = random.choice(tags)
        url = f"https://www.pornhub.com/video/search?search={tag}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        blocks = soup.select("div.videoPreviewBg")

        for vid in blocks[:limit]:
            try:
                title = vid['data-title']
                link = "https://www.pornhub.com" + vid['data-video-url']
                thumb = vid.select_one("img")['src']
                if any(w in title.lower() for w in ['gay', 'yaoi', 'trap']):
                    continue
                results.append({
                    "title": title,
                    "link": link,
                    "thumb": thumb
                })
            except:
                continue
    except Exception as e:
        print(f"[!] Pornhub error: {e}")
    return results
