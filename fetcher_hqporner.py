import requests
from bs4 import BeautifulSoup

def fetch_hqporner(limit=10):
    print("[+] Fetching from HQPorner...")
    results = []
    try:
        r = requests.get("https://hqporner.com/", timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.pic")

        for item in items:
            try:
                link_tag = item.find("a")
                title = link_tag["title"]
                href = "https://hqporner.com" + link_tag["href"]
                img = "https://hqporner.com" + item.find("img")["src"]

                if any(w in title.lower() for w in ['gay', 'yaoi', 'futanari', 'trap']):
                    continue

                results.append({
                    "title": title,
                    "link": href,
                    "thumb": img
                })

                if len(results) >= limit:
                    break

            except:
                continue

    except Exception as e:
        print(f"[!] HQPorner error: {e}")
    return results
