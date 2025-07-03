import os
import random
import praw
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

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
    "cosplay": ["nsfwcosplay", "cosplaygirls", "SexyCosplayGirls", "NSFWCostumes", "lewdcosplay", "cosplaybabes"],
    "cosplayx": ["nsfwcosplay", "cosplaybutts", "realcosplaygonewild", "perfectcosplay", "naughtycospics"],
    "reddit_all": ["GoneWild", "NSFW_GIF", "Creampies", "realgirls", "AnalGW", "PetiteGoneWild", "cumsluts"],
    "gif": ["NSFW_GIF", "NSFW_GIFS", "PornGifs", "HighQualityGifs", "NSFW_Porn_GIF", "60fpsporn", "AnalGifs"],
    "creampie": ["Creampies", "cumsluts", "AnalGW"],
    "facial": ["facial", "cumsluts", "cumonclothes"],
    "milf": ["MilfGW", "amateur_milfs", "milf", "maturemilf"],
    "ass": ["ass", "assinthong", "pawgtastic", "BigBooty"],
    "facesitting": ["facesitting", "face_sitting"],
    "tightsfuck": ["PantyhoseGirls", "leggingsgonewild"],
    "posing": ["NSFW_Glamour", "JustHotGirls"],
    "realhot": ["RealGirls", "NSFW_Video", "NSFW_Snapchat"],
    "rawass": ["bareass", "RealGirls", "butt"],
    "perfectcos": ["cosplaygirls", "cosplaybabes", "SexyCosplayGirls"],
    "video": ["RealGirls", "NSFW_Video", "NSFW_Snapchat", "HighQualityGifs"]
}

BANNED_WORDS = ["futanari", "gay", "yaoi", "trap", "dickgirl", "svg", "tiff", "dick", "dickpick"]

def is_direct_media(url):
    valid_ext = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm"]
    return any(url.lower().endswith(ext) for ext in valid_ext)

def sanitize_url(url):
    url = url.lower()
    if url.endswith(".gifv"):
        url = url.replace(".gifv", ".mp4")
    return url

def fetch_reddit_sync(limit=50, sort=None, target="reddit_all", tag=None):
    print(f"[DEBUG] fetch_reddit_sync() target={target}, sort={sort}, tag={tag}")
    results = []
    subreddits = SUBREDDITS.get(target, [])
    if not subreddits:
        print("[DEBUG] Nessun subreddit trovato per questo target.")
        return []

    chosen = random.sample(subreddits, min(len(subreddits), 5))

    for sub in chosen:
        try:
            final_sort = sort or random.choice(["hot", "top", "new"])
            time_filter = random.choice(["day", "week", "month", "year", "all"])

            if final_sort == "top":
                posts = reddit.subreddit(sub).top(time_filter=time_filter, limit=limit * 2)
            elif final_sort == "hot":
                posts = reddit.subreddit(sub).hot(limit=limit * 2)
            else:
                posts = reddit.subreddit(sub).new(limit=limit * 2)

            for post in posts:
                print(f"[DEBUG] Controllo post: {post.title} | {post.url}")

                if not post.over_18 or post.is_self:
                    print("[DEBUG] Scartato: non è over 18 o è selfpost")
                    continue

                url = sanitize_url(post.url)
                title = post.title.lower()

                # Se v.redd.it cerco di prendere il video diretto
                if "v.redd.it" in url:
                    try:
                        url = post.media["reddit_video"]["fallback_url"]
                        print(f"[DEBUG] Video diretto v.redd.it: {url}")
                    except (KeyError, TypeError):
                        print("[DEBUG] Scartato: v.redd.it senza video diretto")
                        continue

                if not is_direct_media(url):
                    print(f"[DEBUG] Scartato: non è media diretto - {url}")
                    continue

                if any(bad in title for bad in BANNED_WORDS):
                    print(f"[DEBUG] Scartato: parola bannata trovata in {title}")
                    continue

                if tag and tag.lower() not in title:
                    continue

                results.append({
                    "title": post.title,
                    "link": url,
                    "thumb": url,
                    "ext": url.split('.')[-1]
                })

                if len(results) >= limit:
                    break

        except Exception as e:
            print(f"[!] Reddit error in {sub}: {e}")

    print(f"[DEBUG] fetch_reddit_sync() trovati {len(results)} risultati.")
    return results

async def fetch_reddit(limit=50, sort=None, target="reddit_all", tag=None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, fetch_reddit_sync, limit, sort, target, tag)
