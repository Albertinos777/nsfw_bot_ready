import requests
from bs4 import BeautifulSoup

def fetch_spankbang(limit=10):
    print("[+] Fetching from SpankBang...")
    results = []
    try:
        url = "https://spankbang.com/s/creampie+facial+cosplay"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        videos = soup.select("div.video_item")

        for vid in videos[:limit * 2]:
            try:
                title = vid.select_one(".video_title").text.strip()
                link = "https://spankbang.com" + vid.select_one("a")["href"]
                thumb = vid.select_one("img")["src"]
                if any(w in title.lower() for w in ['gay', 'yaoi', 'trap']):
                    continue
                results.append({
                    "title": title,
                    "link": link,
                    "thumb": thumb
                })
                if len(results) >= limit:
                    break
            except:
                continue
    except Exception as e:
        print(f"[!] SpankBang error: {e}")
    return results
