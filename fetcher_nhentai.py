import requests
from bs4 import BeautifulSoup

def fetch_nhentai(limit=10):
    print("[+] Fetching from nhentai...")
    results = []
    page = 1

    while len(results) < limit:
        url = f"https://nhentai.net/?page={page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        gallery_items = soup.select('.gallery')

        for item in gallery_items:
            if len(results) >= limit:
                break

            title = item.select_one('.caption').text.strip()
            link = "https://nhentai.net" + item.select_one('a')['href']
            img_tag = item.select_one('img')
            cover = img_tag.get('data-src') if img_tag.has_attr('data-src') else img_tag.get('src')

            # Vai alla pagina singola del doujin per leggere i tag
            try:
                doujin_page = requests.get(link)
                doujin_soup = BeautifulSoup(doujin_page.text, 'html.parser')
                tag_elements = doujin_soup.select('.tag-container .name')
                tags = [t.text.lower() for t in tag_elements]
            except:
                tags = []

            # Filtri
            if any(t in tags for t in ['futanari', 'yaoi', 'male:male', 'bl']):
                continue

            if 'full color' not in ' '.join(tags):
                continue

            results.append({
                'title': title,
                'link': link,
                'thumb': cover
            })

        page += 1

    return results
