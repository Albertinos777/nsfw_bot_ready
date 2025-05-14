import requests
from xml.etree import ElementTree

def fetch_rule34(limit=10):
    print("[+] Fetching from rule34...")
    results = []
    page = 0
    collected = 0

    while collected < limit:
        url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&pid={page}&tags=rating:explicit"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()

            if not r.content.strip().startswith(b'<?xml'):
                print("[!] Risposta non XML valida da rule34.")
                break

            root = ElementTree.fromstring(r.content)
            posts = root.findall('post')

            for post in posts:
                if collected >= limit:
                    break
                tags = post.attrib.get('tags', '').lower()
                if 'futanari' in tags or 'yaoi' in tags or 'male/male' in tags:
                    continue
                img_url = post.attrib.get('file_url')
                if img_url and img_url.endswith(('.jpg', '.png', '.gif', '.webm')):
                    results.append({
                        'title': tags[:50] + '...',
                        'link': img_url,
                        'thumb': img_url
                    })
                    collected += 1
        except Exception as e:
            print(f"[!] Errore rule34: {e}")
            break

        page += 1

    return results
