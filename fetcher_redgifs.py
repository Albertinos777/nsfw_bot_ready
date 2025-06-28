import requests
import random

def fetch_redgifs(limit=10):
    print("[DEBUG] fetch_redgifs migliorato")
    results = []
    token = ""

    # Ottieni token API pubblico
    try:
        r = requests.post("https://api.redgifs.com/v2/auth/temporary")
        token = r.json().get("token")
    except Exception as e:
        print(f"[!] RedGIFs token error: {e}")
        return results

    headers = {"Authorization": f"Bearer {token}"}
    tags = ["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"]

    try:
        for _ in range(limit * 2):
            tag = random.choice(tags)
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=100"

            r = requests.get(url, headers=headers)
            if not r.ok:
                continue

            data = r.json()
            for item in data.get("gifs", []):
                video = item["urls"].get("hd") or item["urls"].get("gif")
                if video and video.endswith(".mp4"):
                    results.append({
                        "title": item.get("title", f"RedGIFs: {tag}"),
                        "link": video,
                        "thumb": item["urls"].get("thumbnail", video),
                        "ext": "mp4"
                    })
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] RedGIFs error: {e}")

    return results
