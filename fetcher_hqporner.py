import requests
from bs4 import BeautifulSoup

def fetch_hqporner(limit=10):
    print(f"[DEBUG] fetch_hqporner()")
    results = []
    base_url = "https://hqporner.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(f"{base_url}/hd-porn-videos.html", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("div.racy > a")

        for a in links:
            if len(results) >= limit:
                break

            href = a["href"]
            full_link = base_url + href
            page = requests.get(full_link, headers=headers, timeout=10)
            psoup = BeautifulSoup(page.text, "html.parser")

            video_tag = psoup.find("video")
            source = video_tag.find("source") if video_tag else None
            mp4 = source["src"] if source else ""

            if not mp4 or not mp4.endswith(".mp4"):
                continue

            title = psoup.find("title").text.strip().replace(" - HQPorner.com", "")
            results.append({
                "title": title,
                "link": mp4,
                "thumb": "",
                "ext": "mp4"
            })

    except Exception as e:
        print(f"[!] HQPorner error: {e}")

    return results
