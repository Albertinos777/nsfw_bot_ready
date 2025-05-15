import requests
from bs4 import BeautifulSoup

def fetch_toonily(limit=10):
    print(f"[DEBUG] fetch_toonily() chiamato (limit={limit})")
    results = []
    url = "https://toonily.com/genre/adult/"

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.utao")

        for c in cards:
            if len(results) >= limit:
                break

            a = c.select_one("a")
            img = c.select_one("img")

            if not a or not img:
                continue

            link = a['href']
            title = a.get("title") or img.get("alt", "Manhwa")
            thumb = img.get("src")

            if any(x in title.lower() for x in ['yaoi', 'bl', 'shota']):
                continue

            results.append({
                "title": title.strip(),
                "link": link,
                "thumb": thumb,
                "ext": "jpg"
            })

    except Exception as e:
        print(f"[!] Errore toonily: {e}")

    print(f"[DEBUG] Toonily trovati: {len(results)}")
    return results
