import requests
from bs4 import BeautifulSoup

def fetch_txxx(limit=10):
    print(f"[DEBUG] fetch_txxx() limit={limit}")
    results = []
    base_url = "https://www.txxx.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(f"{base_url}/best/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("div.thumb-inside a[href^='/videos/']")

        for a in links:
            if len(results) >= limit:
                break

            href = a.get("href")
            video_page = base_url + href
            vr = requests.get(video_page, headers=headers, timeout=10)
            vsoup = BeautifulSoup(vr.text, "html.parser")

            title_tag = vsoup.find("title")
            title = title_tag.text.strip().replace(" - TXXX.COM", "") if title_tag else "TXXX Video"

            video = vsoup.find("video")
            source = video.find("source", type="video/mp4") if video else None
            mp4 = source.get("src") if source else None

            if not mp4:
                continue

            if any(bad in title.lower() for bad in ['gay', 'yaoi', 'futanari']):
                continue

            results.append({
                'title': title,
                'link': mp4,
                'thumb': a.find("img")["src"] if a.find("img") else "",
                'ext': 'mp4'
            })

    except Exception as e:
        print(f"[!] txxx error: {e}")

    return results
