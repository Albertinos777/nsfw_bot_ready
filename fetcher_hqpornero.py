import requests
from bs4 import BeautifulSoup

def fetch_hqpornero(limit=10, tag=""):
    print("[DEBUG] fetch_hqpornero()")
    results = []
    page = 1

    while len(results) < limit and page <= 5:
        url = f"https://hqpornero.com/page/{page}/"
        if tag:
            url = f"https://hqpornero.com/tag/{tag}/page/{page}/"

        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.select("article")

            for a in articles:
                if len(results) >= limit:
                    break

                title_elem = a.select_one("h2.entry-title a")
                video_page_url = title_elem["href"]
                title = title_elem.text.strip()

                # Vai alla pagina del video per estrarre link diretto
                try:
                    vr = requests.get(video_page_url, timeout=10)
                    vsoup = BeautifulSoup(vr.text, "html.parser")
                    iframe = vsoup.find("iframe")
                    if iframe and "src" in iframe.attrs:
                        video_embed_url = iframe["src"]
                        # Alcuni link di embed diretti
                        if video_embed_url.endswith(".mp4"):
                            results.append({
                                "title": title,
                                "link": video_embed_url,
                                "thumb": a.select_one("img")["src"],
                                "ext": "mp4"
                            })
                except Exception as ve:
                    print(f"[!] Errore video page {video_page_url}: {ve}")
                    continue

        except Exception as e:
            print(f"[!] Errore hqpornero page {page}: {e}")

        page += 1

    return results
