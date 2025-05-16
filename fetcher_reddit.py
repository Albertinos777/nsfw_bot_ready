import praw
import os
import random

def is_valid_reddit_link(url):
    return (
        url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm')) and
        "gifv" not in url and
        "redgifs.com" not in url and
        "imgur.com/a/" not in url
    )

def fetch_reddit(limit=20, sort="hot", target="reddit_all", tag=None):
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
        "cosplay": ["nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes", "lewdcosplay", "cosplaybabes"],
        "cosplayx": ["nsfwcosplay", "cosplayonoff", "cosplaybutts", "cosplayboobs", "cosplaynsfw"],
        "reddit_all": ["GoneWild", "NSFW_GIF", "cumsluts", "Creampies", "PetiteGoneWild", "AssGifs", "boobbounce", "nsfw_hd", "realgirls"],
        "gif": ["NSFW_GIF", "AssGifs", "cumsluts", "analgifs"],
        "creampie": ["Creampies", "cumsluts", "AnalGW"],
        "facial": ["cumsluts", "GirlsFinishingTheJob"],
        "milf": ["milf", "HotMILFs", "RealMilfs", "maturemilf", "Milf_Gifs"],
        "ass": ["AssGifs", "pawgtastic", "ass", "asstastic", "analgw"],
        "facesitting": ["facesitting", "face_sit", "nsfwfacesitting"],
        "tightsfuck": ["tightsfuck", "pantyhose", "pantyfetish", "nylongirls"],
        "posing": ["nsfwposing", "nakedposing", "sexyposing"],
        "realhot": ["realgirls", "NSFW_Snapchat", "GirlsInLingerie"],
        "rawass": ["AssGifs", "pawgtastic", "RealGirls"],
        "perfectcos": ["cosplaygirls", "cosplaybabes", "lewdcosplay"]
    }

    chosen_subs = subreddits.get(target, [])
    if not chosen_subs:
        return []

    random.shuffle(chosen_subs)
    for sub in chosen_subs:
        try:
            subreddit = reddit.subreddit(sub)
            if sort == "hot":
                posts = subreddit.hot(limit=100)
            elif sort == "new":
                posts = subreddit.new(limit=100)
            else:
                posts = subreddit.top(time_filter="month", limit=100)

            for post in posts:
                url = post.url
                title = post.title

                if not is_valid_reddit_link(url):
                    continue
                if tag and tag.lower() not in title.lower():
                    continue
                if post.over_18 and not post.is_self:
                    results.append({
                        'title': title,
                        'link': url,
                        'thumb': url,
                        'ext': url.split('.')[-1]
                    })
                    if len(results) >= limit:
                        return results
        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")
            continue

    return results
