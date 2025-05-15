import random

def fetch_audio(limit=3):
    print("[+] Fetching audio hentai...")
    samples = [
        {
            "title": "Maid ASMR Roleplay",
            "link": "https://files.catbox.moe/abcd12.mp3",
            "thumb": ""
        },
        {
            "title": "Lewd Moaning Loop",
            "link": "https://files.catbox.moe/xyz987.mp3",
            "thumb": ""
        },
        {
            "title": "NSFW Audio Girl Moaning",
            "link": "https://files.catbox.moe/moanshot.mp3",
            "thumb": ""
        }
    ]
    return random.sample(samples, min(limit, len(samples)))
