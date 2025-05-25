import requests
import random

API_KEY = ""  # puoi anche lasciarlo vuoto

def fetch_eporner(limit=10, keywords="creampie+cosplay+facial+milf"):
    print("[DEBUG] fetch_eporner()")
    results = []
    page = random.randint(1, 20)
    url = f"https://www.eporner.com/api/v2/video/search/?query={keywords}&per_page=40&page={page}&thumbsize=big&order=top-weekly"

    try:
        response = requests.get(url)
        data = response.json()

        for video in data.get("videos", []):
            video_url = video.get("embed")
            title = video.get("title", "Video")
            files = video.get("files", [])
            if not files:
                continue

            file_url = files[0].get("file")
            if not file_url or not file_url.endswith(".mp4"):
                continue

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
