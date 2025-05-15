import requests
from bs4 import BeautifulSoup

def fetch_manhwa(limit=10):
    print(f"[DEBUG] fetch_manhwa()")
    results = []
    url = "https://manga18.club/manga-list?type=topview"  # miglior fonte
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".manga-title")

        for a in cards:
            if len(results) >= limit:
                break

            title = a.text.strip()
            link = a["href"]
            img_tag = a.find_parent("div", class_="manga-box").find("img")
            thumb = img_tag["src"] if img_tag else ""

            if any(bad in title.lower() for bad in ["yaoi", "bl", "futanari", "gay"]):
                continue

            results.append({
                "title": title,
                "link": link,
                "thumb": thumb,
                "ext": "jpg"
            })

    except Exception as e:
        print(f"[!] manhwa fetch error: {e}")

    return results
