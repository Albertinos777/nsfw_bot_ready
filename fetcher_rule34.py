import requests
import xml.etree.ElementTree as ET

def fetch_rule34(limit=10):
    print(f"[DEBUG] fetch_rule34 chiamato con target = {target}")
    print("[+] Fetching from rule34...")
    results = []
    try:
        r = requests.get(f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={limit}&tags=rating:explicit")
        root = ET.fromstring(r.content)

        for post in root.findall("post"):
            file_url = post.attrib.get("file_url", "")
            if any(ext in file_url for ext in [".webm", ".mp4", ".gif", ".jpg", ".png"]):
                results.append({
                    "title": post.attrib.get("tags", "")[:80],
                    "link": file_url,
                    "thumb": file_url,
                    "ext": file_url.split(".")[-1]
                })
    except Exception as e:
        print(f"[!] rule34 error: {e}")
    return results
