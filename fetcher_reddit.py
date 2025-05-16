import os
import random
import praw

REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="nsfw_bot_script",
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    check_for_async=False
)

SUBREDDITS = {
    "cosplay": [
        "nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes", "lewdcosplay", "cosplaybabes"
    ],
    "cosplayx": [
        "nsfwcosplay", "cosplayonlewd", "LewdAnimeCosplay", "HentaiCosplay"
    ],
    "reddit_all": [
        "GoneWild", "NSFW_GIF", "Creampies", "NSFW_Snapchat", "realgirls", "AnalGW", "PetiteGoneWild", "cumsluts"
    ],
    "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs", "boobbounce"],
    "creampie": ["Creampies", "cumsluts", "AnalGW"],
    "facial": ["facial", "cumsluts", "cumonclothes"],
    "milf": ["MilfGW", "amateur_milfs", "milf", "maturemilf"],
    "ass": ["ass", "assinthong", "pawgtastic", "BigBooty"],
    "facesitting": ["facesitting", "face_sitting"],
    "tightsfuck": ["PantyhoseGirls", "leggingsgonewild"],
    "posing": ["NSFW_Glamour", "JustHotGirls"],
    "realhot": ["RealGirls", "NSFW_Video", "NSFW_Snapchat"],
    "rawass": ["bareass", "RealGirls", "butt"],
    "perfectcos": ["cosplaygirls", "cosplaybabes", "SexyCosplayGirls"]
}

def is_valid_url(url):
    return any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm"])

def fetch_reddit(limit=30, sort=None, target="reddit_all", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, sort={sort}, tag={tag}")
    results = []

    subreddits = SUBREDDITS.get(target, [])
    if not subreddits:
        return []

    chosen = random.sample(subreddits, min(len(subreddits), 4))
    for sub in chosen:
        try:
            final_sort = sort or random.choice(["hot", "top", "new"])
            time_filter = random.choice(["day", "week", "month", "year"])

            if final_sort == "top":
                posts = reddit.subreddit(sub).top(time_filter=time_filter, limit=limit * 2)
            elif final_sort == "hot":
                posts = reddit.subreddit(sub).hot(limit=limit * 2)
            else:
                posts = reddit.subreddit(sub).new(limit=limit * 2)

            for post in posts:
                if not post.over_18 or post.is_self:
                    continue

                url = post.url.lower()
                title = post.title.lower()

                if not is_valid_url(url):
                    continue

                if tag and tag.lower() not in title:
                    continue

                if any(b in title for b in ["futanari", "gay", "yaoi", "trap", "dickgirl"]):
                    continue

                results.append({
                    "title": post.title,
                    "link": post.url,
                    "thumb": post.url,
                    "ext": post.url.split(".")[-1]
                })

                if len(results) >= limit:
                    break

        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")

    return results
