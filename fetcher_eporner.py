import requests
import random
import re
import time


def extract_mp4(video_page_url):
    try:
        r = requests.get(video_page_url, headers={"User-Agent": "Mozilla/5.0"})
        if not r.ok:
            print(f"[!] Errore caricamento pagina: {r.status_code}")
            return None

        matches = re.findall(r'"https:\\/\\/cdn\.eporner\.com\\/videos\\/[^\"]+\.mp4"', r.text)

        if matches:
            link = matches[0].replace('\\/', '/')
            return link

    except Exception as e:
        print(f"[!] Errore estrazione mp4: {e}")

    return None


def fetch_eporner(limit=10):
    results = []
    try:
        for _ in range(limit * 5):  # Più tentativi per video validi
            tag = random.choice(["creampie", "milf", "teen", "public", "ass", "blowjob", "big tits", "cosplay"])
            url = f"https://www.eporner.com/api/v2/video/search/?keywords={tag}&per_page=50&order=top-weekly&thumbsize=big&gay=0&lq=1&page=1"

            r = requests.get(url)

            if not r.ok:
                print(f"[!] Richiesta fallita {r.status_code}")
                continue

            data = r.json()
            for item in data.get("videos", []):
                page_link = item.get("url")
                thumb = item.get("default_thumb")
                title = item.get("title", "Eporner")

                mp4_link = extract_mp4(page_link)
                if mp4_link and mp4_link.endswith(".mp4"):
                    results.append({
                        "title": title,
                        "link": mp4_link,
                        "thumb": thumb,
                        "ext": "mp4"
                    })

                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] Errore fetch_eporner: {e}")

    return results
