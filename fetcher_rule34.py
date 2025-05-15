import requests
from xml.etree import ElementTree

def fetch_rule34(limit=10):
    print("[+] Fetching from rule34...")
    results = []
    try:
        url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={limit}&tags=rating:explicit"
        r = requests.get(url, timeout=10)
        root = ElementTree.fromstring(r.content)
        for child in root:
            tags = child.attrib.get('tags', '')
            if 'file_url' in child.attrib and not any(tag in tags for tag in ['futanari', 'yaoi', 'gay', 'trap']):
                results.append({
                    'title': tags[:100],
                    'link': child.attrib['file_url'],
                    'thumb': child.attrib['file_url']
                })
    except Exception as e:
        print(f"[!] Errore Rule34: {e}")
    return results
