import praw
import requests

def fetch_reddit(limit=10):
    print("[+] Fetching from Reddit...")
    results = []

    reddit = praw.Reddit(
        client_id="-mNY__Ksg3bA2DSH2XQ0OA",
        client_secret="JbkgeIlsleFAMz_SXWPG1anP6z4Pvw",
        user_agent="nsfw_collector by /u/Lopsided-List-4516",
        username="Lopsided-List-4516",
        password="V3mGqsA22Y4kv2M",
        check_for_async=False
    )

    subreddits = ["RealGirls", "NSFW_GIF", "porninfifteenseconds", "holdthemoan", "nsfwcosplay", "GoneWild", "AsiansGoneWild", "GoneWild30Plus", "PetiteGoneWild", "Rule34LoL", "CelebNSFW", "cumsluts", "creampies", "analgw", "pawg", "nsfwhardcore", "nsfwoutfits", "hentai", "HentaiSource", "Rule34LoL", "ecchi"]
    for sub in subreddits:
        try:
            for post in reddit.subreddit(sub).hot(limit=limit * 3):  # overfetching per filtrarli
                if post.over_18 and not post.is_self:
                    url = post.url.lower()
                    if any(ext in url for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm', '.mp3']):
                        try:
                            head = requests.head(post.url, timeout=5)
                            if head.status_code == 200:
                                results.append({
                                    'title': f"{sub} - {post.title[:40]}",
                                    'link': post.url,
                                    'thumb': post.url
                                })
                                if len(results) >= limit:
                                    break
                        except:
                            continue
        except Exception as e:
            print(f"[!] Errore su subreddit {sub}: {e}")

    return results
