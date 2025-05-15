import praw
import os
import random
from urllib.parse import urlparse

ALLOWED_HOSTS = ['i.redd.it', 'i.imgur.com', 'cdn.discordapp.com']
ALLOWED_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']

def is_valid_reddit_link(url):
    parsed = urlparse(url)
    if not any(url.endswith(ext) for ext in ALLOWED_EXTS):
        return False
    if not any(host in parsed.netloc for host in ALLOWED_HOSTS):
        return False
    if 'v.redd.it' in url or 'redgifs.com' in url:
        return False
    return True

def fetch_reddit(limit=10, sort="hot", target=None):
    if not target:
        raise ValueError("Target is required")

    print(f"[+] Fetching Reddit ({target})...")
    results = []

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot",
        check_for_async=False
    )

    subreddits = {
        "cosplay": [
            "nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes",
            "lewdcosplay", "cosplaybabes", "cosplaybutts"
        ],
        "reddit_all": [
            "GoneWild", "cumsluts", "NSFW_GIF", "Creampies", "AssGifs",
            "PetiteGoneWild", "nsfw_hd", "AnalGW", "porninfifteenseconds",
            "boobbounce", "realgirls", "NSFW_Snapchat", "Wild_Hardcore"
        ],
        "gif": [
            "NSFW_GIF", "porninfifteenseconds", "AssGifs", "boobbounce"
        ],
        "creampie": [
            "Creampies", "cumsluts", "analcreampie", "pussycreampies"
        ],
        "facial": [
            "facialcumsluts", "cumsluts", "cumonher", "GirlsFinishingTheJob"
        ],
        "milf": [
            "amateur_milfs", "maturemilf", "MaturePorn", "HotMoms", "RealMature"
        ],
        "ass": [
            "AssGifs", "BigAssPorn", "ass", "booty", "AssOnTwitch"
        ]
    }

    chosen_subs = random.sample(subreddits.get(target, []), min(len(subreddits.get(target, [])), 5))

    for sub in chosen_subs:
        try:
            sort_mode = random.choice(["hot", "new", "top"])
            time_filter = random.choice(["day", "week", "month"])
            posts = reddit.subreddit(sub).top(time_filter=time_filter, limit=limit * 2)

            for post in posts:
                url = post.url.lower()
                title = post.title.lower()

                if not is_valid_reddit_link(url):
                    continue
                if any(w in title for w in ['futanari', 'yaoi', 'trap', 'gay', 'dickgirl']):
                    continue
                if post.over_18 and not post.is_self:
                    results.append({
                        'title': post.title,
                        'link': post.url,
                        'thumb': post.url,
                        'ext': post.url.split('.')[-1]
                    })
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"[!] Reddit error {sub}: {e}")
            continue

    return results
