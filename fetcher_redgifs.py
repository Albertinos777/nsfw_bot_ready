import requests
import random

def fetch_redgifs(limit=10):
    print("[DEBUG] fetch_redgifs()")
    results = []

    try:
        for _ in range(limit * 2):
            tag = random.choice(["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"])
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=100"

            r = requests.get(url)
            if not r.ok:
                continue

            data = r.json()
            for item in data.get("gifs", []):
                video = item["urls"].get("hd", "") or item["urls"].get("gif")
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
        print(f"[!] RedGIFs error: {e}")

    return results
