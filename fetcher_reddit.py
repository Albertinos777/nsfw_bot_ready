import os
import random
import praw

def is_valid_reddit_link(url):
    return url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm'))

def fetch_reddit(limit=30, sort="hot", target="reddit_all"):
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

    subreddits = {
        "cosplay": [
            "nsfwcosplay", "SexyCosplayGirls", "lewdcosplay", "cosplaybabes", "NSFWCostumes"
        ],
        "reddit_all": [
            "NSFW_GIF", "GoneWild", "cumsluts", "Creampies", "PetiteGoneWild",
            "AnalGW", "boobbounce", "NSFW_Snapchat", "realgirls", "Blowjobs"
        ],
        "gif": ["NSFW_GIF", "porninfifteenseconds", "HighResNSFW"],
        "creampie": ["Creampies", "AnalGW", "cumsluts"],
        "facial": ["cumsluts", "facialcumshot", "Blowjobs"],
        "milf": ["milf", "GoneWild30Plus", "HotWives"],
        "ass": ["asstastic", "pawg", "BestBooties"]
    }

    sources = subreddits.get(target, [])
    random.shuffle(sources)

    for sub in sources:
        try:
            subreddit = reddit.subreddit(sub)
            posts = subreddit.top(time_filter=random.choice(["day", "week", "month", "year", "all"]), limit=limit * 3)

            for post in posts:
                url = post.url.lower()
                title = post.title.lower()

                if not is_valid_reddit_link(url):
                    continue
                if any(x in title for x in ['futanari', 'yaoi', 'trap', 'gay']):
                    continue
                if post.over_18 and not post.is_self:
                    results.append({
                        'title': post.title,
                        'link': post.url,
                        'thumb': post.url,
                        'ext': post.url.split('.')[-1]
                    })

                if len(results) >= limit:
                    return results
        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")
            continue

    return results
