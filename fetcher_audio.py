import random

def fetch_audio(limit=3):
    print("[DEBUG] fetch_audio()")
    sources = [
        # Inserisci link diretti a .mp3 di qualità
        ("Lewd Moan 1", "https://cdn.example.com/moan1.mp3"),
        ("Roleplay Audio", "https://cdn.example.com/roleplay.mp3")
    ]
    random.shuffle(sources)
    return [{"title": s[0], "link": s[1]} for s in sources[:limit]]
