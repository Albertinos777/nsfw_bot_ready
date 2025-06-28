# fetcher_eporner.py
import requests
import random
import re
import time

def fetch_eporner(limit=10):
    print("[DEBUG] fetch_eporner() avanzato")
    results = []
    tags = ["creampie", "milf", "cosplay", "anal", "public", "ass"]

    try:
        for _ in range(limit * 2):
            tag = random.choice(tags)
            url = (
                "https://www.eporner.com/api/v2/video/search/"
                f"?query={tag}&per_page=20&page=1&thumbsize=big&order=top-weekly&format=json"
            )
            r = requests.get(url, timeout=10)
            if not r.ok:
                print(f"[!] Errore API Eporner: {r.status_code}")
                continue

            data = r.json()
            for vid in data.get("videos", []):
                page_url = vid.get("url")
                title = vid.get("title", "Eporner")
                thumb = vid.get("default_thumb")
                if not page_url:
                    continue

                pr = requests.get(page_url, timeout=10)
                match = re.search(r'"(https://cdn\.eporner\.com/videos/.*?\.mp4)"', pr.text)
                if match:
                    results.append({
                        "title": title,
                        "link": match.group(1),
                        "thumb": thumb,
                        "ext": "mp4"
                    })
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] Errore fetch_eporner avanzato: {e}")

    return results
