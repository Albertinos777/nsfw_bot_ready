import requests
import random

API_KEY = ""  # Se vuoto, prova comunque, altrimenti registrati su Eporner e metti la chiave

def fetch_eporner(limit=10, keywords="creampie+cosplay+facial+milf"):
    print("[DEBUG] fetch_eporner migliorato")
    results = []
    page = random.randint(1, 20)
    base = f"https://www.eporner.com/api/v2/video/search/?query={keywords}&per_page=40&page={page}&thumbsize=big&order=top-weekly"
    if API_KEY:
        base += f"&api_key={API_KEY}"

    try:
        response = requests.get(base)
        data = response.json()

        for video in data.get("videos", []):
            file_url = video.get("embed_url") or video.get("default_thumb")
            title = video.get("title", "Video")

            if file_url and ".mp4" in file_url:
                results.append({
                    "title": title,
                    "link": file_url,
                    "thumb": video.get("default_thumb"),
                    "ext": "mp4"
                })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] fetch_eporner error: {e}")

    return results
