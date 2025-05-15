import requests
from bs4 import BeautifulSoup

def fetch_nhentai(limit=10):
    print("[+] Fetching from nhentai...")
    results = []
    page = 1
    while len(results) < limit:
        try:
            url = f"https://nhentai.net/?page={page}"
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            gallery_items = soup.select('.gallery')
            for item in gallery_items:
                if len(results) >= limit:
                    break
                title = item.select_one('.caption').text.strip()
                if any(bad in title.lower() for bad in ['futanari', 'yaoi', 'gay', 'trap']):
                    continue
                link = "https://nhentai.net" + item.select_one('a')['href']
                cover = item.select_one('img')['data-src'] if item.select_one('img').has_attr('data-src') else item.select_one('img')['src']
                results.append({
                    'title': title,
                    'link': link,
                    'thumb': cover
                })
            page += 1
        except Exception as e:
            print(f"[!] Errore NHentai: {e}")
            break
    return results
