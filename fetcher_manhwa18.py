import requests
from bs4 import BeautifulSoup

def fetch_manhwa(limit=10):
    print(f"[DEBUG] fetch_manhwa18()")
    results = []
    url = "https://manga18.club/manga-list?genre=all&status=all&type=manhwa"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.manga-box")

        for box in items:
            if len(results) >= limit:
                break

            a = box.find("a", href=True)
            img = box.find("img")
            title = img["alt"].strip() if img else "Manhwa"
            link = a["href"]
            thumb = img["src"] if img else ""

            if any(term in title.lower() for term in ['yaoi', 'bl', 'futanari', 'gay']):
                continue

            results.append({
                "title": title,
                "link": link,
                "thumb": thumb,
                "ext": "jpg"
            })

    except Exception as e:
        print(f"[!] manhwa18 error: {e}")

    return results
