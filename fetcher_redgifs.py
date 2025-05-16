# fetcher_redgifs.py
import requests

def fetch_redgifs(limit=10):
    print("[DEBUG] fetch_redgifs()")
    results = []
    try:
        url = f"https://api.redgifs.com/v2/gifs/search?search=nsfw&count={limit}"
        headers = {"User-Agent": "nsfwbot"}
        response = requests.get(url, headers=headers)
        data = response.json()

        for gif in data.get("gifs", []):
            link = gif["urls"]["hd"]
            results.append({
                "title": gif["title"] or "RedGifs",
                "link": link,
                "thumb": gif["urls"].get("thumbnail", link),
                "ext": "mp4"
            })
    except Exception as e:
        print(f"[!] Errore RedGifs: {e}")
    return results
