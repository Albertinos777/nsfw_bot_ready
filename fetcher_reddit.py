import os
import praw

def is_valid_reddit_link(url):
    banned_ext = ['.gifv', '.tiff', '.svg']
    banned_hosts = ['redgifs.com', 'gfycat.com', 'imgur.com/a/', 'v.redd.it']
    return not any(b in url for b in banned_ext + banned_hosts)

def fetch_reddit(limit=20, sort="hot", target="reddit_all", tag=None):
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
            "nsfwcosplay", "SexyCosplayGirls", "NSFWCostumes", "lewdcosplay", "cosplaybutts"
        ],
        "reddit_all": [
            "GoneWild", "cumsluts", "NSFW_GIF", "Creampies", "AssGifs", "PetiteGoneWild",
            "nsfw_hd", "AnalGW", "porninfifteenseconds", "boobbounce", "realgirls"
        ],
        "gif": ["NSFW_GIF", "porninfifteenseconds"],
        "creampie": ["Creampies", "Creampie_Anal", "Creampie_Gifs"],
        "facial": ["facial", "cumontits", "cumsluts"],
        "milf": ["milf", "maturemilf", "realmilfs"],
        "ass": ["AssGifs", "asstastic", "assholegonewild"],
        "cosplayx": ["NSFWCostumes", "lewdcosplay", "cosplaygirls", "cosplaybutts"],
        "facesitting": ["facesitting", "FaceSitting_GIFS"],
        "tightsfuck": ["Tightdresses", "PantyhoseGirls", "leggingsgonewild"],
        "posing": ["NSFW_Posing", "Hotchicksposing", "RealGirls"],
        "realhot": ["realgirls", "AmateurArchives"],
        "rawass": ["asstastic", "assholegonewild"],
        "perfectcos": ["SexyCosplayGirls", "cosplaybabes"]
    }

    chosen_subs = subreddits.get(target, [])
    if not chosen_subs:
        return []

    for sub in chosen_subs:
        try:
            subreddit = reddit.subreddit(sub)
            posts = getattr(subreddit, sort)(limit=limit * 2)

            for post in posts:
                if post.over_18 and not post.is_self and is_valid_reddit_link(post.url):
                    if any(bad in post.title.lower() for bad in ["futanari", "yaoi", "trap", "dickgirl", "gay"]):
                        continue
                    results.append({
                        "title": post.title,
                        "link": post.url,
                        "thumb": post.url,
                        "ext": post.url.split('.')[-1]
                    })
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")
            continue

    return results
