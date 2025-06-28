import requests
import random
import re

def fetch_eporner(limit=10, keywords="creampie+cosplay+facial+milf"):
    print("[DEBUG] fetch_eporner() avanzato")
    results = []
    page = random.randint(1, 20)
    url = f"https://www.eporner.com/api/v2/video/search/?query={keywords}&per_page=40&page={page}&thumbsize=big&order=top-weekly"

    try:
        r = requests.get(url)
        if not r.ok:
            print(f"[!] Errore richiesta Eporner: {r.status_code}")
            return results

        data = r.json()

        for video in data.get("videos", []):
            page_url = video.get("url")
            title = video.get("title", "Video")
            thumb = video.get("default_thumb")

            if not page_url:
                continue

            try:
                page_res = requests.get(page_url, timeout=10)
                mp4_match = re.search(r'"(https:\/\/cdn\.eporner\.com\/videos\/.*?\.mp4)"', page_res.text)

                if mp4_match:
                    mp4_link = mp4_match.group(1)
                    results.append({
                        "title": title,
                        "link": mp4_link,
                        "thumb": thumb,
                        "ext": "mp4"
                    })

            except Exception as ex:
                print(f"[!] Errore scraping video: {ex}")

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] Eporner fetch error: {e}")

    return results
