import requests
from bs4 import BeautifulSoup

def fetch_spankbang(limit=10):
    print(f"[DEBUG] fetch_spankbang() chiamato (limit={limit})")
    base_url = "https://spankbang.party"
    search_url = f"{base_url}/videos?o=trending"
    results = []

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select("div.video-item > a")

        for a in links:
            if len(results) >= limit:
                break

            href = a.get("href")
            if not href or "/video/" not in href:
                continue

            video_page = base_url + href
            title = a.get("title", "SpankBang")
            thumb = a.select_one("img")
            thumb_url = thumb.get("data-src") or thumb.get("src") if thumb else ""

            # Scarica la pagina video per estrarre link .mp4
            try:
                vr = requests.get(video_page, headers=headers, timeout=10)
                vsoup = BeautifulSoup(vr.text, "html.parser")
                script_tags = vsoup.find_all("script")

                for s in script_tags:
                    if "mp4" in s.text and "https://" in s.text:
                        start = s.text.find("https://")
                        end = s.text.find(".mp4") + 4
                        mp4_url = s.text[start:end]
                        if mp4_url.endswith(".mp4"):
                            results.append({
                                "title": title,
                                "link": mp4_url,
                                "thumb": thumb_url,
                                "ext": "mp4"
                            })
                            break
            except Exception as e:
                print(f"[!] Errore parsing video: {e}")
                continue

    except Exception as e:
        print(f"[!] Errore SpankBang main: {e}")

    print(f"[DEBUG] SpankBang ha trovato {len(results)} video validi")
    return results
