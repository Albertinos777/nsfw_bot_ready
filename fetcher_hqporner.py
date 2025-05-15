import requests
from bs4 import BeautifulSoup

def fetch_hqporner(limit=10):
    print(f"[DEBUG] fetch_hqporner() chiamato (limit={limit})")
    base_url = "https://hqporner.com"
    results = []

    try:
        r = requests.get(f"{base_url}/categories/creampie.html", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        videos = soup.select("div.video-item")

        for item in videos:
            if len(results) >= limit:
                break

            a = item.select_one("a")
            if not a:
                continue

            link = base_url + a.get("href")
            title = a.get("title") or "HQPorner"
            thumb = item.select_one("img")
            thumb_url = thumb.get("data-src") or thumb.get("src")

            if any(x in title.lower() for x in ['gay', 'yaoi', 'futanari']):
                continue

            # HQPorner non fornisce .mp4 diretto → mostriamo il link
            results.append({
                "title": title,
                "link": link,
                "thumb": thumb_url,
                "ext": "html"  # fallback, viene trattato come documento
            })

    except Exception as e:
        print(f"[!] Errore HQPorner: {e}")

    print(f"[DEBUG] fetch_hqporner ha trovato {len(results)} risultati")
    return results
