import requests
from bs4 import BeautifulSoup
import random

def fetch_xvideos(limit=10):
    print("[+] Fetching from XVideos...")
    base_url = "https://www.xvideos.com"
    tags = ["creampie", "facial", "cosplay", "blowjob", "amateur"]
    results = []

    try:
        tag = random.choice(tags)
        url = f"{base_url}/tags/{tag}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        videos = soup.select("div.thumb-block")

        for vid in videos:
            if len(results) >= limit:
                break
            try:
                link = base_url + vid.select_one("a")["href"]
                title = vid.select_one(".title").text.strip()
                thumb = vid.select_one("img")["data-src"]
                if any(bad in title.lower() for bad in ['futanari', 'yaoi', 'gay', 'trap']):
                    continue
                results.append({
                    "title": title,
                    "link": link,
                    "thumb": thumb
                })
            except:
                continue
    except Exception as e:
        print(f"[!] XVideos error: {e}")
    return results
