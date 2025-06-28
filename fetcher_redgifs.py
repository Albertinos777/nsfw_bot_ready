import requests
import random
import time

REDGIFS_TOKEN = None
REDGIFS_LAST_REFRESH = 0


def refresh_redgifs_token():
    global REDGIFS_TOKEN, REDGIFS_LAST_REFRESH
    try:
        res = requests.post("https://api.redgifs.com/v2/auth/temporary")
        data = res.json()
        REDGIFS_TOKEN = data.get("token")
        REDGIFS_LAST_REFRESH = time.time()
        print(f"[INFO] RedGIFs token aggiornato.")
    except Exception as e:
        print(f"[!] Errore aggiornamento token RedGIFs: {e}")


def fetch_redgifs(limit=10):
    global REDGIFS_TOKEN, REDGIFS_LAST_REFRESH

    # Controlla se il token va aggiornato (dopo 6 ore)
    if not REDGIFS_TOKEN or (time.time() - REDGIFS_LAST_REFRESH > 6 * 3600):
        refresh_redgifs_token()
        if not REDGIFS_TOKEN:
            print("[!] Token RedGIFs non disponibile.")
            return []

    print("[DEBUG] fetch_redgifs()")
    results = []

    try:
        for _ in range(limit * 3):  # Più tentativi per trovare contenuti validi
            tag = random.choice(["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"])
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=100"

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
        print(f"[!] RedGIFs fetch error: {e}")

    return results
