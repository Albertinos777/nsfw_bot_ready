import requests
import random
import time

REDGIFS_TOKEN = None
REDGIFS_LAST_REFRESH = 0


def refresh_redgifs_token():
    global REDGIFS_TOKEN, REDGIFS_LAST_REFRESH
    try:
        res = requests.post("https://api.redgifs.com/v2/auth/temporary")
        res.raise_for_status()
        data = res.json()
        REDGIFS_TOKEN = data.get("token")
        REDGIFS_LAST_REFRESH = time.time()
        print(f"[INFO] Token RedGIFs aggiornato.")
    except Exception as e:
        print(f"[!] Errore aggiornamento token RedGIFs: {e}")
        REDGIFS_TOKEN = None


def fetch_redgifs(limit=10):
    global REDGIFS_TOKEN, REDGIFS_LAST_REFRESH

    if not REDGIFS_TOKEN or (time.time() - REDGIFS_LAST_REFRESH > 5 * 3600):
        refresh_redgifs_token()
        if not REDGIFS_TOKEN:
            print("[!] Token RedGIFs non disponibile.")
            return []

    print("[DEBUG] Fetch RedGIFs attivo.")
    results = []

    try:
        for _ in range(limit * 3):
            tag = random.choice(["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"])
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=50"

            headers = {"Authorization": f"Bearer {REDGIFS_TOKEN}"}
            r = requests.get(url, headers=headers)
            if not r.ok:
                print(f"[!] RedGIFs richiesta fallita: {r.status_code}")
                continue

            data = r.json()
            for item in data.get("gifs", []):
                video = item["urls"].get("hd") or item["urls"].get("gif")
                if video and video.endswith(".mp4"):
                    results.append({
                        "title": item.get("title", f"RedGIFs: {tag}"),
                        "link": video,
                        "thumb": item.get("urls", {}).get("thumbnail", video),
                        "ext": "mp4"
                    })
                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] RedGIFs errore fetch: {e}")

    return results
