import requests
from xml.etree import ElementTree

def fetch_rule34(limit=10):
    print(f"[DEBUG] fetch_rule34() chiamato (limit={limit})")
    results = []
    r = requests.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={limit}&tags=rating:explicit")

    try:
        root = ElementTree.fromstring(r.content)
    except Exception as e:
        print(f"[!] Errore parsing XML Rule34: {e}")
        return results

    for post in root.findall("post"):
        file_url = post.get("file_url")
        if not file_url:
            continue

        if any(ext in file_url for ext in ['.webm', '.gifv', '.svg', '.tiff']):
            continue

        if any(bad in file_url.lower() for bad in ['futanari', 'yaoi', 'trap', 'dickgirl', 'gay']):
            continue

        results.append({
            'title': "Rule34",
            'link': file_url,
            'thumb': file_url,
            'ext': file_url.split('.')[-1]
        })

    print(f"[DEBUG] fetch_rule34 ha trovato {len(results)} risultati")
    return results
