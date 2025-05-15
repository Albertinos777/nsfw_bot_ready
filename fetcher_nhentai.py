import requests
from bs4 import BeautifulSoup

def fetch_nhentai(limit=10):
    print(f"[DEBUG] fetch_nhentai() chiamato (limit={limit})")
    results = []
    page = 1

    while len(results) < limit and page <= 10:
        url = f"https://nhentai.net/?page={page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        gallery_items = soup.select('.gallery')

        for item in gallery_items:
            if len(results) >= limit:
                break

            title_tag = item.select_one('.caption')
            link_tag = item.select_one('a')
            img_tag = item.select_one('img')

            if not (title_tag and link_tag and img_tag):
                continue

            title = title_tag.text.strip()
            link = "https://nhentai.net" + link_tag['href']
            cover = img_tag.get('data-src') or img_tag.get('src')

            # Filtro
            if any(bad in title.lower() for bad in ['futanari', 'yaoi', 'gay']):
                continue

            # Se non è a colori
            if 'full color' not in title.lower():
                continue

            results.append({
                'title': title,
                'link': link,
                'thumb': cover,
                'ext': cover.split('.')[-1]
            })

        page += 1

    print(f"[DEBUG] fetch_nhentai ha trovato {len(results)} risultati")
    return results
