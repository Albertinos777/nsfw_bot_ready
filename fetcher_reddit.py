import praw
import os
import random

def fetch_reddit(limit=10, sort="new", target="cosplay"):
    print(f"[+] Fetching Reddit /{target}...")
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

        # Subreddit diversi per tipo
        subreddits = {
            "cosplay": [
                "nsfwcosplay", "cosplaygirls", "sexycosplay", "CosplayBoobs",
                "CosplayButts", "cosplaybabes", "nsfwcosplaygw"
            ],
            "hentai": [
                "hentai", "rule34", "ecchi", "UncensoredHentai", "Hentai_GIF"
            ],
            "real": [
                "RealGirls", "NSFW_GIF", "GoneWild", "cumsluts", "Creampies"
            ]
        }

        chosen_subs = subreddits.get(target, subreddits["cosplay"])
        random.shuffle(chosen_subs)

        for sub in chosen_subs:
            try:
                posts = getattr(reddit.subreddit(sub), sort)(limit=limit * 2)
                for post in posts:
                    title = post.title.lower()
                    url = post.url.lower()
                    if any(w in title or w in url for w in ['futanari', 'yaoi', 'trap', 'gay']):
                        continue
                    if post.over_18 and not post.is_self:
                        if any(ext in post.url for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm']):
                            results.append({
                                'title': f"{sub} - {post.title[:100]}",
                                'link': post.url,
                                'thumb': post.url,
                                'ext': post.url.split('.')[-1]
                            })
                            if len(results) >= limit:
                                break
            except Exception as e:
                print(f"[!] Reddit error {sub}: {e}")
                continue

    except Exception as e:
        print(f"[!] Reddit setup error: {e}")

    return results
