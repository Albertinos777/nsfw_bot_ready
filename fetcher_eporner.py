import requests
import random

def fetch_eporner(limit=10, keywords="creampie+cosplay+facial+milf"):
    print("[DEBUG] fetch_eporner()")
    results = []
    page = random.randint(1, 20)
    url = f"https://www.eporner.com/api/v2/video/search/?query={keywords}&per_page=40&page={page}&thumbsize=big&order=top-weekly"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for video in data.get("videos", []):
            title = video.get("title", "Video")
            files = video.get("files", [])

            # Cerco il file mp4 migliore disponibile
            file_url = None
            for f in files:
                if f.get("file", "").endswith(".mp4"):
                    file_url = f.get("file")
                    break

            if not file_url:
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
