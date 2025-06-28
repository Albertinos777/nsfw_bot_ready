import requests
import random

def fetch_redgifs(limit=10):
    print("[DEBUG] fetch_redgifs()")
    results = []

    try:
        # Prima ottengo un token anonimo
        token_res = requests.get("https://api.redgifs.com/v2/auth/temporary")
        token = token_res.json().get("token", "")

        if not token:
            print("[!] Impossibile ottenere token RedGIFs")
            return results

        headers = {"Authorization": f"Bearer {token}"}

        for _ in range(limit * 3):  # Più tentativi per trovare contenuti validi
            tag = random.choice(["nsfw", "creampie", "cosplay", "facial", "milf", "blowjob", "ass", "public"])
            url = f"https://api.redgifs.com/v2/gifs/search?search_text={tag}&order=trending&count=50"

            r = requests.get(url, headers=headers)
            if not r.ok:
                continue

            data = r.json()
            for item in data.get("gifs", []):
                video = item.get("urls", {}).get("hd", "") or item.get("urls", {}).get("gif")
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
