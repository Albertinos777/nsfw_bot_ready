import requests
from bs4 import BeautifulSoup

def fetch_txxx(limit=10):
    print(f"[DEBUG] fetch_txxx()")
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = "https://www.txxx.com"

    try:
        res = requests.get(f"{base_url}/videos/", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("div.thumb-inside a[href^='/videos/']")

        for a in links:
            if len(results) >= limit:
                break

            href = a.get("href")
            video_page = base_url + href

            try:
                vr = requests.get(video_page, headers=headers, timeout=10)
                vsoup = BeautifulSoup(vr.text, "html.parser")

                # Alternative: JSON or og:video parsing
                mp4 = ""
                og_video = vsoup.find("meta", property="og:video")
                if og_video and og_video.get("content"):
                    mp4 = og_video["content"]

                if not mp4.endswith(".mp4"):
                    continue

                title = vsoup.title.text.replace(" - TXXX.COM", "").strip()

                if any(bad in title.lower() for bad in ['gay', 'yaoi', 'futanari']):
                    continue

                results.append({
                    'title': title,
                    'link': mp4,
                    'thumb': a.find("img")["src"] if a.find("img") else "",
                    'ext': 'mp4'
                })

            except Exception as e:
                print(f"[!] Errore video interno: {e}")
                continue

    except Exception as e:
        print(f"[!] Errore fetch_txxx: {e}")

    return results
