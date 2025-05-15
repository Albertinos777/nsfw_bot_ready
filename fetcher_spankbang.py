import requests
from bs4 import BeautifulSoup

def fetch_spankbang(limit=10):
    print(f"[DEBUG] fetch_spankbang() chiamato (limit={limit})")
    results = []
    base = "https://spankbang.party"

    try:
        r = requests.get(f"{base}/videos?o=trending", timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(r.text, "html.parser")
        thumbs = soup.select("div.video-item")

        for video in thumbs:
            if len(results) >= limit:
                break

            a = video.find("a", href=True)
            img = video.find("img")

            if not a or not img:
                continue

            vid_link = base + a["href"]
            thumb = img["src"]
            title = img.get("alt", "SpankBang")

            if any(x in title.lower() for x in ['gay', 'futanari', 'trap']):
                continue

            results.append({
                "title": title,
                "link": vid_link,
                "thumb": thumb,
                "ext": "mp4"  # assume mp4 for preview
            })

    except Exception as e:
        print(f"[!] Errore fetch_spankbang: {e}")

    print(f"[DEBUG] SpankBang trovati: {len(results)}")
    return results
