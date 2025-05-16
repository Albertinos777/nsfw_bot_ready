# fetcher_e621.py
import requests

def fetch_e621(limit=10, tag="female"):
    print("[DEBUG] fetch_e621()")
    results = []
    try:
        url = f"https://e621.net/posts.json?tags={tag}+rating:explicit&limit={limit}"
        headers = {
            "User-Agent": "nsfwbot (by user)",
        }
        response = requests.get(url, headers=headers)
        posts = response.json().get("posts", [])
        for post in posts:
            file = post.get("file", {})
            if not file.get("url"):
                continue
            link = file["url"]
            ext = link.split('.')[-1]
            results.append({
                "title": post.get("tags", {}).get("general", ["E621"])[0],
                "link": link,
                "thumb": link,
                "ext": ext
            })
    except Exception as e:
        print(f"[!] Errore e621: {e}")
    return results
