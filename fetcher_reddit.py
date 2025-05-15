import praw
import os

def fetch_reddit(limit=10, sort="hot"):
    print("[+] Fetching from Reddit...")
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

        subreddits = [
            "hentai", "nsfwcosplay", "rule34", "RealGirls", "NSFW_GIF",
            "ecchi", "UncensoredHentai", "GoneWild", "cumsluts"
        ]

        for sub in subreddits:
            try:
                posts = getattr(reddit.subreddit(sub), sort)(limit=limit * 2)
                for post in posts:
                    title = post.title.lower()
                    url = post.url.lower()
                    if any(word in title for word in ['futanari', 'yaoi', 'gay', 'trap']) or any(word in url for word in ['futanari', 'yaoi', 'gay', 'trap']):
                        continue
                    if post.over_18 and not post.is_self:
                        if any(ext in post.url.lower() for ext in ['.jpg', '.png', '.gif', '.mp4', '.webm']):
                            results.append({
                                'title': f"{sub} - {post.title[:100]}",
                                'link': post.url,
                                'thumb': post.url
                            })
                            if len(results) >= limit:
                                break
            except Exception as e:
                print(f"[!] Reddit error {sub}: {e}")
                continue

    except Exception as e:
        print(f"[!] Reddit setup error: {e}")

    return results
