import praw
import os
import random

from dotenv import load_dotenv
load_dotenv()

def is_valid_reddit_link(url):
    return any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm'])

def fetch_reddit(limit=50, target="cosplay", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, tag={tag}")

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot by u/yourbot",
        check_for_async=False
    )

    results = []

    subreddit_map = {
        "cosplay": ["nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes", "lewdcosplay"],
        "reddit_all": ["GoneWild", "NSFW_GIF", "PetiteGoneWild", "cumsluts", "RealGirls", "AssGifs", "AnalGW"],
        "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs"],
        "creampie": ["Creampies", "cumsluts", "CreampieGifs"],
        "facial": ["cumsluts", "GirlsFinishingTheJob"],
        "milf": ["amateur_milfs", "milf", "GoneWild30Plus"],
        "ass": ["ass", "paag", "AssGifs"],
        "cosplayx": ["cosplaygirls", "SexyCosplayGirls", "cosplaybutts", "lewdcosplay"],
        "facesitting": ["facesitting", "Smothering"],
        "tightsfuck": ["PantyhoseGW", "tights", "UpskirtGW"],
        "posing": ["PetiteGoneWild", "nsfwposing"],
        "realhot": ["RealGirls", "NSFW_Snapchat"],
        "rawass": ["ass", "tightdresses"],
        "perfectcos": ["SexyCosplayGirls", "lewdcosplay", "NSFWCostumes"],
    }

    chosen_subs = subreddit_map.get(target, ["nsfw"])
    random.shuffle(chosen_subs)

    banned_keywords = ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl', 'loli']

    try:
        for sub in chosen_subs:
            subreddit = reddit.subreddit(sub)

            sort_mode = random.choice(["hot", "top", "new"])
            time_filter = random.choice(["day", "week", "month", "year", "all"])

            print(f"[DEBUG] Searching subreddit: r/{sub} | sort: {sort_mode} | time: {time_filter}")

            if sort_mode == "top":
                posts = subreddit.top(limit=limit * 2, time_filter=time_filter)
            elif sort_mode == "new":
                posts = subreddit.new(limit=limit * 2)
            else:
                posts = subreddit.hot(limit=limit * 2)

            for post in posts:
                if post.over_18 and not post.is_self:
                    title = post.title.lower()
                    url = post.url.lower()

                    if any(b in title for b in banned_keywords):
                        continue
                    if tag and tag.lower() not in title and tag.lower() not in url:
                        continue
                    if not is_valid_reddit_link(url):
                        continue

                    results.append({
                        'title': post.title,
                        'link': post.url,
                        'thumb': post.url,
                        'ext': post.url.split('.')[-1].split("?")[0]
                    })

                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[!] Reddit error in fetch_reddit(): {e}")

    return results
