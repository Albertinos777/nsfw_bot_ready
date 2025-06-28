import requests
import random
import time

REDGIFS_TOKEN = None
REDGIFS_LAST_REFRESH = 0

def refresh_redgifs_token():
    global REDGIFS_TOKEN, REDGIFS_LAST_REFRESH
    try:
        r = requests.post("https://api.redgifs.com/v2/auth/temporary")
        if r.ok:
            REDGIFS_TOKEN = r.json().get("token")
            REDGIFS_LAST_REFRESH = time.time()
            print("[INFO] RedGIFs token aggiornato.")
        else:
            print(f"[!] RedGIFs token error: {r.status_code}")
    except Exception as e:
        print(f"[!] RedGIFs refresh error: {e}")

def fetch_redgifs(limit=10):
    global REDGIFS_TOKEN
    if not REDGIFS_TOKEN or (time.time() - REDGIFS_LAST_REFRESH > 5 * 3600):
        refresh_redgifs_token()
    if not REDGIFS_TOKEN:
        print("[!] RedGIFs token non disponibile.")
        return []

    try:
        results = []
        for _ in range(limit * 3):
            tag = random.choice(["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"])
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=100"
            headers = {"Authorization": f"Bearer {REDGIFS_TOKEN}"}
            r = requests.get(url, headers=headers)

            if not r.ok:
                continue

            for item in r.json().get("gifs", []):
                link = item["urls"].get("hd") or item["urls"].get("gif")
                if link and link.endswith(".mp4"):
                    results.append({
                        "title": item.get("title", tag),
                        "link": link,
                        "thumb": item["urls"].get("thumbnail", link),
                        "ext": "mp4"
                    })
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        print(f"[!] Errore fetch_redgifs: {e}")
        return []
