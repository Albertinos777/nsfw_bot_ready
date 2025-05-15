import requests
from bs4 import BeautifulSoup
import random

def fetch_nhentai(limit=10):
    print("[+] Fetching from nhentai...")
    results = []
    page = random.randint(1, 20)
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
            img = item.select_one('img')
            thumb = img['data-src'] if img.has_attr('data-src') else img['src']

            if any(tag in title.lower() for tag in ['futanari', 'yaoi']) or 'full color' not in title.lower():
                continue

            results.append({
                'title': title,
                'link': link,
                'thumb': thumb
            })
        except:
            continue

    return results
