import praw
import os
import random

def is_valid_reddit_link(url):
    return url.endswith((".mp4", ".gif", ".jpg", ".jpeg", ".png", ".webm"))

def fetch_reddit(limit=40, sort="hot", target="gif", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, sort={sort}")
    results = []

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot",
        check_for_async=False
    )

    subreddits_map = {
        "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs"],
        "creampie": ["Creampies", "analcreampie"],
        "facial": ["cumfetish", "facialcumsluts"],
        "milf": ["milf", "MilfandCum"],
        "ass": ["ass", "tightass", "asstastic"],
        "cosplay": ["nsfwcosplay", "cosplaybabes"],
        "reddit_all": ["GoneWild", "NSFW_Snapchat", "realgirls", "PetiteGoneWild"],
        "cosplayx": ["nsfwcosplay", "cosplaybabes", "SexyCosplayGirls", "cosplaygirls"],
        "perfectcos": ["NSFWCostumes", "lewdcosplay", "cosplaybutts"],
        "rawass": ["ass", "asstastic", "booty", "assholegonewild"],
        "facesitting": ["facesitting", "FaceSittingGW", "asslicking"],
        "tightsfuck": ["pantyhose", "TightShorts", "leggingsgonewild"],
        "posing": ["PetiteGoneWild", "ass", "gonewildcurvy"],
        "realhot": ["realgirls", "Amateur", "gonewild", "NSFW_Snapchat"]
    }

    subs = subreddits_map.get(target, ["GoneWild"])
    chosen = random.sample(subs, min(3, len(subs)))

    for sub in chosen:
        try:
            subreddit = reddit.subreddit(sub)
            posts = getattr(subreddit, sort)(limit=limit)
            for post in posts:
                if post.over_18 and not post.is_self and is_valid_reddit_link(post.url):
                    results.append({
                        "title": post.title,
                        "link": post.url,
                        "thumb": post.url,
                        "ext": post.url.split('.')[-1]
                    })
        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")
    return results
