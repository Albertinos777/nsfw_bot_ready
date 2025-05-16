import os
import praw
import random

def fetch_reddit(limit=10, sort="hot", target="reddit_all", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, sort={sort}, tag={tag}")
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
            "lewdcosplay", "cosplaybutts"
        ],
        "reddit_all": [
            "GoneWild", "cumsluts", "NSFW_GIF", "Creampies", "AssGifs",
            "PetiteGoneWild", "nsfw_hd", "AnalGW", "porninfifteenseconds",
            "boobbounce", "realgirls", "NSFW_Snapchat", "Wild_Hardcore"
        ]
    }

    subs = subreddits.get(target, subreddits["reddit_all"])
    chosen = random.sample(subs, min(len(subs), 4))

    for sub in chosen:
        try:
            subreddit = reddit.subreddit(sub)
            posts = getattr(subreddit, sort)(limit=limit * 2)
            for post in posts:
                url = post.url.lower()
                title = post.title.lower()

                if tag and tag not in title:
                    continue
                if not post.over_18 or post.is_self or post.score < 500:
                    continue
                if any(bad in url for bad in ['.gifv', '.svg', '.tiff']):
                    continue
                if any(bad in title for bad in ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl']):
                    continue

                ext = url.split('.')[-1]
                results.append({
                    'title': post.title,
                    'link': post.url,
                    'thumb': post.url,
                    'ext': ext
                })
                if len(results) >= limit:
                    return results
        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")
            continue

    return results
