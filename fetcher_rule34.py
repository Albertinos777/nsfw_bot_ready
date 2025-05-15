import requests
from xml.etree import ElementTree

def fetch_rule34(limit=20):
    print(f"[DEBUG] fetch_rule34()")
    results = []

    try:
        r = requests.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={limit*2}", timeout=10)
        root = ElementTree.fromstring(r.content)

        for child in root:
            file_url = child.attrib.get("file_url")
            tags = child.attrib.get("tags", "")
            if not file_url or any(tag in tags for tag in ['futanari', 'yaoi', 'gay']):
                continue

            results.append({
                'title': tags.split()[0] if tags else "rule34",
                'link': file_url,
                'thumb': file_url,
                'ext': file_url.split('.')[-1]
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] rule34 error: {e}")

    return results
