import os
import praw
import random

def is_valid_reddit_link(url):
    allowed_exts = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']
    return any(url.lower().endswith(ext) for ext in allowed_exts)

def fetch_reddit(limit=10, sort="hot", target="cosplay", tag=None):
    print(f"[DEBUG] fetch_reddit() target={target}, sort={sort}")
    results = []

    try:
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
            "gif": ["NSFW_GIF", "porninfifteenseconds", "AssGifs", "boobbounce"],
            "creampie": ["Creampies", "AnalGW"],
            "facial": ["cumsluts", "facialcumshots"],
            "milf": ["milf", "amateur_milfs", "MilfGoneWild"],
            "ass": ["ass", "assholegonewild", "RealGirls", "NSFWAss"],
            "cosplayx": ["lewdcosplay", "cosplaygirls", "NSFWCostumes"],
            "facesitting": ["facesitting", "FaceSittingGW"],
            "tightsfuck": ["pantyhose", "tights", "GirlsInTights"],
            "posing": ["NSFW_Pose", "sexygirls", "NSFW_Glamour"],
            "realhot": ["NSFW_Snapchat", "Wild_Hardcore"],
            "rawass": ["assholegonewild", "NSFWAss"],
            "perfectcos": ["SexyCosplayGirls", "cosplaybabes"]
        }

        chosen_subs = subreddits.get(target, [])
        random.shuffle(chosen_subs)

        for sub in chosen_subs:
            try:
                # Vari random sort + time filter per pescare da sempre
                sort_mode = random.choice(["hot", "top", "new"])
                time_filter = random.choice(["all", "year", "month", "week", "day"])

                if sort_mode == "top":
                    posts = reddit.subreddit(sub).top(time_filter=time_filter, limit=limit * 2)
                elif sort_mode == "new":
                    posts = reddit.subreddit(sub).new(limit=limit * 2)
                else:
                    posts = reddit.subreddit(sub).hot(limit=limit * 2)

                for post in posts:
                    url = post.url.lower()
                    title = post.title.lower()

                    if not is_valid_reddit_link(url):
                        continue
                    if any(w in title for w in ['futanari', 'yaoi', 'trap', 'gay', 'dickgirl']):
                        continue
                    if tag and tag not in title:
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
                print(f"[!] Reddit error in {sub}: {e}")
                continue

    except Exception as e:
        print(f"[!] Reddit setup error: {e}")

    print(f"[DEBUG] fetch_reddit returned {len(results)} results for target={target}")
    return results
