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
        links = soup.select("div.thumb-inside a")

        for a in links:
            if len(results) >= limit:
                break

            href = a.get("href")
            if not href or not href.startswith("/videos/"):
                continue

            video_page = base_url + href
            vr = requests.get(video_page, headers=headers, timeout=10)
            vsoup = BeautifulSoup(vr.text, "html.parser")
            title = vsoup.find("title").text.strip().replace(" - TXXX.COM", "")
            video_tag = vsoup.find("video")

            if not video_tag:
                continue

            mp4 = video_tag.find("source", {"type": "video/mp4"})
            if not mp4:
                continue

            mp4_url = mp4.get("src")
            thumb_tag = vsoup.find("meta", {"property": "og:image"})
            thumb = thumb_tag["content"] if thumb_tag else ""

            if any(x in title.lower() for x in ['gay', 'yaoi', 'futanari', 'trap']):
                continue

            results.append({
                "title": title,
                "link": mp4_url,
                "thumb": thumb,
                "ext": "mp4"
            })

    except Exception as e:
        print(f"[!] txxx error: {e}")

    return results
