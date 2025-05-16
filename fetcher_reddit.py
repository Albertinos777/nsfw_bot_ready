import os
import praw
import random

def is_valid_reddit_link(url):
    valid_ext = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']
    return any(url.lower().endswith(ext) for ext in valid_ext)

def fetch_reddit(limit=20, sort="hot", target="reddit_all", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, sort={sort}")
    results = []

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot by u/Albertinos777",
        check_for_async=False
    )

    subreddits = {
        "cosplay": [
            "nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes",
            "lewdcosplay", "cosplaybabes", "cosplaybutts"
        ],
        "cosplayx": [
            "cosplaycumsluts", "cumcosplay", "cosplaycreampie"
        ],
        "reddit_all": [
            "GoneWild", "cumsluts", "NSFW_GIF", "Creampies", "AssGifs",
            "PetiteGoneWild", "nsfw_hd", "AnalGW", "porninfifteenseconds",
            "boobbounce", "realgirls", "NSFW_Snapchat", "Wild_Hardcore"
        ],
        "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs"],
        "creampie": ["Creampies", "CreampieGirls", "CreampieInsideMe"],
        "facial": ["facial", "FacialGifs", "GirlsFinishingTheJob"],
        "milf": ["nsfwmilf", "maturemilf", "LegalTeensAndMoms"],
        "ass": ["ass", "pawg", "AnalGW"],
        "facesitting": ["facesitting", "FaceSittingPics", "Facesitting_Gifs"],
        "tightsfuck": ["girlsinyogapants", "TightDresses", "leggingsgonewild"],
        "posing": ["assholegonewild", "facedownassup", "doggystyle"],
        "realhot": ["realgirls", "LegalTeensXXX", "CollegeInitiation"],
        "rawass": ["pawg", "AssholeGoneWild", "amateurcumsluts"],
        "perfectcos": ["NSFWCostumes", "cosplaygirls", "SexyCosplayGirls"]
    }

    selected_subs = subreddits.get(target, [])
    random.shuffle(selected_subs)
    selected_subs = selected_subs[:min(5, len(selected_subs))]

    for sub in selected_subs:
        try:
            subreddit = reddit.subreddit(sub)
            if sort == "new":
                posts = subreddit.new(limit=limit * 2)
            elif sort == "top":
                posts = subreddit.top(limit=limit * 2, time_filter="year")
            else:
                posts = subreddit.hot(limit=limit * 2)

            for post in posts:
                if not post.over_18 or post.is_self:
                    continue
                url = post.url
                title = post.title

                if tag and tag not in title.lower():
                    continue
                if not is_valid_reddit_link(url):
                    continue
                if any(bad in title.lower() for bad in ['futanari', 'yaoi', 'trap', 'gay', 'dickgirl']):
                    continue

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
