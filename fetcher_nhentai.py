import requests
from bs4 import BeautifulSoup
import random

def fetch_nhentai(limit=10):
    print("[+] Fetching from nhentai...")
    results = []
    page = random.randint(1, 25)
    url = f"https://nhentai.net/?page={page}"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.text, 'html.parser')
    gallery_items = soup.select('.gallery')

    for item in gallery_items:
        if len(results) >= limit:
            break
        try:
            title = item.select_one('.caption').text.strip()
            link = "https://nhentai.net" + item.select_one('a')['href']
            img_tag = item.select_one('img')
            cover = img_tag['data-src'] if img_tag.has_attr('data-src') else img_tag['src']
            title_lower = title.lower()

            if any(x in title_lower for x in ['futanari', 'yaoi']):
                continue
            if 'full color' not in title_lower:
                continue

            results.append({
                'title': title,
                'link': link,
                'thumb': cover
            })
        except:
            continue

    return results
