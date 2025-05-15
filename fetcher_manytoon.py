import requests
from bs4 import BeautifulSoup

def fetch_manytoon(limit=10):
    print(f"[DEBUG] fetch_manytoon() limit={limit}")
    results = []
    url = "https://manytoon.com/genre/mature/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.bs")

        for card in cards:
            if len(results) >= limit:
                break

            a = card.find("a", href=True)
            img = card.find("img")

            if not a or not img:
                continue

            title = img.get("alt", "Manhwa").strip()
            link = a["href"]
            thumb = img.get("src")

            if any(x in title.lower() for x in ['yaoi', 'bl', 'gay', 'futanari']):
                continue

            results.append({
                "title": title,
                "link": link,
                "thumb": thumb,
                "ext": "jpg"
            })

    except Exception as e:
        print(f"[!] manytoon error: {e}")

    return results
