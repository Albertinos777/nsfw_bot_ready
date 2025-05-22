import requests

def fetch_e621(limit=10, tag="female"):
    print("[DEBUG] fetch_e621()")
    results = []
    try:
        url = f"https://e621.net/posts.json?tags={tag}+rating:explicit&limit={limit}"
        headers = {
            "User-Agent": "nsfwbot (by user)",
        }
        # Aggiunto timeout
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Solleva un'eccezione per codici di stato HTTP errati
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
    except requests.exceptions.RequestException as req_e:
        print(f"[!] Errore di rete/HTTP e621: {req_e}")
    except ValueError as json_e:
        print(f"[!] Errore JSON e621: {json_e}")
    except Exception as e:
        print(f"[!] Errore generico e621: {e}")
    return results

