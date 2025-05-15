import requests
from bs4 import BeautifulSoup

def fetch_nhentai(limit=20):
    print(f"[DEBUG] fetch_nhentai() limit={limit}")
    results = []
    page = 1

    while len(results) < limit and page <= 10:
        try:
            r = requests.get(f"https://nhentai.net/?page={page}", timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            gallery = soup.select('.gallery')

            for item in gallery:
                if len(results) >= limit:
                    break

                title = item.select_one('.caption').text.strip()
                if any(x in title.lower() for x in ['futanari', 'yaoi', 'trap', 'gay']):
                    continue

                a = item.find("a", href=True)
                img = item.find("img")
                if not a or not img:
                    continue

                results.append({
                    'title': title,
                    'link': "https://nhentai.net" + a['href'],
                    'thumb': img.get("data-src") or img.get("src"),
                    'ext': 'jpg'
                })

            page += 1

        except Exception as e:
            print(f"[!] nhentai error: {e}")
            break

    return results
