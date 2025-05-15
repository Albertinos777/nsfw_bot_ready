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
        blocks = soup.select("li.videoBox")

        for block in blocks[:limit * 2]:
            try:
                a_tag = block.find("a", class_="js-video-title")
                if not a_tag: continue
                title = a_tag.get("title")
                link = "https://www.pornhub.com" + a_tag.get("href")
                thumb = block.find("img")["data-thumb_url"]
                if any(w in title.lower() for w in ['gay', 'yaoi', 'trap']):
                    continue
                results.append({
                    "title": title,
                    "link": link,
                    "thumb": thumb
                })
                if len(results) >= limit:
                    break
            except:
                continue
    except Exception as e:
        print(f"[!] Pornhub error: {e}")
    return results
