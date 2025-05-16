import requests
import random
from bs4 import BeautifulSoup

def fetch_eporner(limit=10, tags=["creampie", "cosplay", "milf", "facial"]):
    print("[DEBUG] fetch_eporner()")
    results = []
    try:
        base_url = "https://www.eporner.com/api/v2/video/search/"
        tag = random.choice(tags)
        params = {
            "query": tag,
            "per_page": limit,
            "thumbsize": "big",
            "page": random.randint(1, 20),
            "sort": "top-week",
            "lq": "0"
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(base_url, params=params, headers=headers)
        if r.status_code == 200 and "videos" in r.json():
            for vid in r.json()["videos"]:
                if not vid.get("embed"):
                    results.append({
                        "title": vid["title"],
                        "link": vid["default_url"],
                        "thumb": vid["image"],
                        "ext": "mp4"
                    })
    except Exception as e:
        print(f"[!] fetch_eporner() error: {e}")

    return results
