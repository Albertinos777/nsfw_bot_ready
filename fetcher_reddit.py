import os
import praw
import requests

def fetch_reddit(limit=10, sort="hot"):
    print("[+] Fetching from Reddit...")
    results = []

    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        user_agent="nsfwbot",
        check_for_async=False
    )

    subreddits = [
        "hentai", "nsfwcosplay", "RealGirls",
        "NSFW_GIF", "GoneWild", "cumsluts",
        "rule34", "ecchi", "UncensoredHentai"
    ]

    for sub in subreddits:
        try:
            subreddit = reddit.subreddit(sub)
            posts = getattr(subreddit, sort)(limit=limit * 3)  # overfetch

            for post in posts:
                if post.over_18 and not post.is_self:
                    if any(ext in post.url.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm']):
                        results.append({
                            'title': f"{sub} - {post.title[:40]}",
                            'link': post.url,
                            'thumb': post.url
                        })
                        if len(results) >= limit:
                            break
        except Exception as e:
            print(f"[!] Reddit error on {sub}: {e}")
            continue

    return results
