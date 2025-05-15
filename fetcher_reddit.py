import praw
import os
import random
from urllib.parse import urlparse

# Host supportati da Telegram
ALLOWED_HOSTS = [
    'i.redd.it', 'i.imgur.com', 'cdn.discordapp.com',
    'media.discordapp.net', 'media.giphy.com'
]

# Estensioni supportate
ALLOWED_EXTS = ['.mp4', '.webm', '.gif', '.jpg', '.jpeg', '.png']

# Filtra URL inutilizzabili
def is_valid_reddit_link(url):
    parsed = urlparse(url)
    if not any(url.endswith(ext) for ext in ALLOWED_EXTS):
        return False
    if not any(host in parsed.netloc for host in ALLOWED_HOSTS):
        return False
    if 'v.redd.it' in url or 'redgifs.com' in url:
        return False
    return True

def fetch_reddit(limit=15, sort="hot", target=None):
    if not target:
        raise ValueError("Target subreddit is required.")

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot",
        check_for_async=False
    )

    subreddits = {
        "cosplay": ["nsfwcosplay", "SexyCosplayGirls", "cosplaybabes"],
        "reddit_all": ["GoneWild", "cumsluts", "Creampies", "NSFW_GIF", "RealGirls"],
        "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs", "boobbounce"],
        "creampie": ["Creampies", "analcreampie", "cumsluts", "pussycreampies"],
        "facial": ["facialcumsluts", "cumonher", "GirlsFinishingTheJob"],
        "milf": ["MaturePorn", "HotMoms", "RealMature", "amateur_milfs"],
        "ass": ["AssGifs", "BigAssPorn", "booty", "AssOnTwitch"]
    }

    chosen_subs = random.sample(subreddits.get(target, []), min(len(subreddits.get(target, [])), 4))
    results = []

    for sub in chosen_subs:
        try:
            sort_mode = random.choice(["hot", "top", "new"])
            time_filter = random.choice(["day", "week", "month"])
            posts = reddit.subreddit(sub).top(time_filter=time_filter, limit=limit * 2)

            for post in posts:
                url = post.url.lower()
                title = post.title.lower()

                if not is_valid_reddit_link(url):
                    continue
                if any(w in title for w in ['futanari', 'yaoi', 'gay', 'trap']):
                    continue
                if post.over_18 and not post.is_self:
                    ext = url.split('.')[-1]
                    results.append({
                        "title": post.title,
                        "link": url,
                        "thumb": url,
                        "ext": ext
                    })
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"[!] Reddit error: {e}")
            continue

    return results
