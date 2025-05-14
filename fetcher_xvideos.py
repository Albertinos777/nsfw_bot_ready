import requests
from bs4 import BeautifulSoup

def fetch_xvideos(limit=5):
    print("[+] Fetching from XVideos...")
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = "https://www.xvideos.com/channels/hentai"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    blocks = soup.select('.thumb-block')

    for block in blocks:
        if len(results) >= limit:
            break
        a_tag = block.select_one('a')
        title_tag = block.select_one('.title')
        img_tag = block.select_one('img')

        if a_tag and title_tag:
            title = title_tag.text.strip()
            link = "https://www.xvideos.com" + a_tag['href']
            thumb = img_tag.get('data-src') if img_tag and img_tag.has_attr('data-src') else (img_tag.get('src') if img_tag else "")

            # Skip futanari/yaoi come da filtro
            if "futanari" in title.lower() or "yaoi" in title.lower():
                continue

            # Aggiungi immagine solo se disponibile
            results.append({
                'title': title,
                'link': link,
                'thumb': thumb if thumb else "https://img.icons8.com/color/200/no-image.png"
            })

    return results
