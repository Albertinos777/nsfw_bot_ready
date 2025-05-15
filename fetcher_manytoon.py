import requests
from bs4 import BeautifulSoup

def fetch_manytoon(limit=10):
    print(f"[DEBUG] fetch_manytoon()")
    results = []
    url = "https://manytoon.com/genre/mature/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
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
            thumb = img["src"]

            if any(term in title.lower() for term in ['yaoi', 'bl', 'futanari', 'gay']):
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
