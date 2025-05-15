import os
import json
import threading
import time
import random
import sys
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_hqporner import fetch_hqporner
from fetcher_audio import fetch_audio

TOKEN = os.environ.get("TOKEN")
print(f"[DEBUG] TOKEN ENV: {TOKEN}")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

CACHE_FILES = {
    "hentai": "cache_hentai.json",
    "cosplay": "cache_cosplay.json",
    "real": "cache_real.json",
    "porno": "cache_porno.json",
    "reddit_all": "cache_reddit.json",
    "gif": "cache_gif.json",
    "creampie": "cache_creampie.json",
    "facial": "cache_facial.json",
    "milf": "cache_milf.json",
    "ass": "cache_ass.json"
}

FAV_FILE = "favorites.json"
loop_enabled = {}

# --------------- UTIL ------------------

def load_cache(mode):
    file = CACHE_FILES[mode]
    if os.path.exists(file):
        with open(file, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(mode, cache):
    with open(CACHE_FILES[mode], "w") as f:
        json.dump(list(cache), f)

def load_favorites():
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    return []

def save_favorite(item):
    favs = load_favorites()
    if item not in favs:
        favs.append(item)
        with open(FAV_FILE, "w") as f:
            json.dump(favs, f)

def is_banned(title_or_url):
    banned = ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl', 'gifv', 'svg', 'tiff']
    return any(bad in title_or_url.lower() for bad in banned)

def send_real(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, "📡 Cerco video reali da Reddit...")

    results = fetch_reddit(limit=20, sort="top", target="reddit_all")
    cache = load_cache("real")
    sent = 0

    for item in results:
        if item['link'] in cache or is_banned(item['title'] + item['link']):
            continue
        send_media(context.bot, chat_id, item)
        cache.add(item['link'])
        sent += 1
        if sent >= 10:
            break

    save_cache("real", cache)
    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="❌ Nessun contenuto trovato su Reddit.")

def send_porno(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, "📡 Cerco video da HQPorner...")

    results = fetch_hqporner(limit=10)
    cache = load_cache("porno")
    sent = 0

    for item in results:
        if item['link'] in cache or is_banned(item['title'] + item['link']):
            continue
        send_media(context.bot, chat_id, item)
        cache.add(item['link'])
        sent += 1
        if sent >= 10:
            break

    save_cache("porno", cache)
    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="❌ Nessun contenuto trovato su HQPorner.")

def send_media(bot, chat_id, item):
    ext = item.get("ext", item['link'].split('.')[-1].lower())
    link = item['link']
    caption = f"{item['title'][:100]}\n🔗 {link}"

    try:
        if ext in ['mp4', 'webm']:
            bot.send_video(chat_id=chat_id, video=link, caption=caption, timeout=30)
        elif ext in ['gif']:
            bot.send_animation(chat_id=chat_id, animation=link, caption=caption, timeout=30)
        elif ext in ['jpg', 'jpeg', 'png']:
            bot.send_photo(chat_id=chat_id, photo=link, caption=caption, timeout=30)
        else:
            bot.send_document(chat_id=chat_id, document=link, caption=caption, timeout=30)
    except Exception as e:
        print(f"[!] Errore nel caricamento media: {e}")
        bot.send_message(chat_id=chat_id, text=f"🔗 {caption}")


# --------------- HANDLERS ------------------

def send_content(update: Update, context: CallbackContext, mode="hentai"):
    print(f"[DEBUG] Entrato in send_content() con mode = {mode}")
    sys.stdout.flush()
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, f"📡 Cerco contenuti per /{mode}...")

    cache = load_cache(mode)
    results = []

    try:
        if mode == "hentai":
            results += fetch_nhentai(limit=20)
            results += fetch_rule34(limit=20)

        elif mode == "cosplay":
            results += fetch_reddit(limit=30, sort="new", target="cosplay")

        elif mode == "real":
            results += fetch_hqporner(limit=15)
            if not results:
                results += fetch_reddit(limit=20, sort="top", target="reddit_all")

        elif mode in ["reddit_all", "gif", "creampie", "facial", "milf", "ass"]:
            results += fetch_reddit(limit=30, sort=random.choice(["hot", "top", "new"]), target=mode)

        else:
            context.bot.send_message(chat_id=chat_id, text="❌ Comando non supportato.")
            return

        random.shuffle(results)
        sent = 0

        for item in results:
            if item['link'] in cache or is_banned(item['title'] + item['link']):
                continue
            send_media(context.bot, chat_id, item)
            cache.add(item['link'])
            sent += 1
            if sent >= 10:
                break

        save_cache(mode, cache)

        if sent == 0:
            context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")

    except Exception as e:
        import traceback
        print(f"\n[!] Errore in send_content({mode}):\n{traceback.format_exc()}\n")
        context.bot.send_message(chat_id=chat_id, text=f"⚠️ Errore nel caricamento contenuti.")


def reset_cache(update: Update, context: CallbackContext):
    for mode in CACHE_FILES:
        with open(CACHE_FILES[mode], "w") as f:
            json.dump([], f)
    update.message.reply_text("✅ Tutte le cache svuotate.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Benvenuto! Comandi disponibili:\n"
        "/new\n/hentai\n/cosplay\n/real (da Reddit)\n/porno (da HQPorner)\n"
        "/reddit\n/audio\n/gif\n/creampie\n/facial\n/milf\n/ass\n"
        "/loopon\n/loopoff\n/resetcache\n/fav <link>\n/favorites\n/random <tag>"
    )


def cmd_new(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, "🎁 Ecco una selezione mista per te...")

    for mode in ["hentai", "cosplay", "real", "reddit_all", "gif", "creampie", "facial", "milf", "ass", "porno"]:
        try:
            send_content(update, context, mode)
            time.sleep(1)  # leggera pausa per non far crashare Telegram
        except Exception as e:
            print(f"[!] Errore in /new per {mode}: {e}")


def send_audio(update: Update, context: CallbackContext):
    results = fetch_audio(limit=3)
    for item in results:
        try:
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=item['link'], caption=item['title'])
        except:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Errore audio:\n{item['link']}")

def add_fav(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("❌ Devi fornire il link del contenuto.")
        return
    link = args[0]
    save_favorite({"title": "Preferito", "link": link, "thumb": link})
    update.message.reply_text("⭐️ Salvato nei preferiti!")

def list_fav(update: Update, context: CallbackContext):
    favs = load_favorites()
    if not favs:
        update.message.reply_text("📭 Nessun contenuto nei preferiti.")
        return
    for item in favs[-10:]:
        send_media(context.bot, update.effective_chat.id, item)

def random_tag(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Esempio: /random creampie")
        return
    tag = context.args[0].lower()
    cache = load_cache("reddit_all")
    results = fetch_reddit(limit=40, sort="hot", target="reddit_all")
    for item in results:
        if tag not in item['title'].lower() or item['link'] in cache:
            continue
        send_media(context.bot, update.effective_chat.id, item)
        cache.add(item['link'])
        save_cache("reddit_all", cache)
        return
    update.message.reply_text("❌ Nessun risultato trovato.")

# --------------- LOOP ------------------

def loop_worker(chat_id):
    while loop_enabled.get(chat_id, False):
        for mode in ["hentai", "cosplay", "real", "reddit_all"]:
            try:
                cache = load_cache(mode)
                results = []
                if mode == "hentai":
                    results += fetch_nhentai(limit=5)
                    results += fetch_rule34(limit=5)
                elif mode == "cosplay":
                    results += fetch_reddit(limit=5, sort="new", target="cosplay")
                elif mode == "real":
                    results += fetch_hqporner(limit=5)
                elif mode == "reddit_all":
                    results += fetch_reddit(limit=5, sort="hot", target="reddit_all")
                for item in results:
                    if item['link'] in cache or is_banned(item['title'] + item['link']):
                        continue
                    send_media(bot, chat_id, item)
                    cache.add(item['link'])
                    save_cache(mode, cache)
                    break
            except Exception as e:
                print(f"[!] Loop error: {e}")
        time.sleep(3600)

def loop_on(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    loop_enabled[chat_id] = True
    update.message.reply_text("🔁 Loop automatico attivato.")
    threading.Thread(target=loop_worker, args=(chat_id,), daemon=True).start()

def loop_off(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    loop_enabled[chat_id] = False
    update.message.reply_text("⛔ Loop disattivato.")

# --------------- DISPATCH ------------------

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("new", cmd_new))
dispatcher.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
dispatcher.add_handler(CommandHandler("cosplay", lambda u, c: send_content(u, c, "cosplay")))
dispatcher.add_handler(CommandHandler("reddit", lambda u, c: send_content(u, c, "reddit_all")))
dispatcher.add_handler(CommandHandler("resetcache", reset_cache))
dispatcher.add_handler(CommandHandler("loopon", loop_on))
dispatcher.add_handler(CommandHandler("loopoff", loop_off))
dispatcher.add_handler(CommandHandler("fav", add_fav))
dispatcher.add_handler(CommandHandler("favorites", list_fav))
dispatcher.add_handler(CommandHandler("random", random_tag))
dispatcher.add_handler(CommandHandler("audio", send_audio))
dispatcher.add_handler(CommandHandler("gif", lambda u, c: send_content(u, c, "gif")))
dispatcher.add_handler(CommandHandler("creampie", lambda u, c: send_content(u, c, "creampie")))
dispatcher.add_handler(CommandHandler("facial", lambda u, c: send_content(u, c, "facial")))
dispatcher.add_handler(CommandHandler("milf", lambda u, c: send_content(u, c, "milf")))
dispatcher.add_handler(CommandHandler("ass", lambda u, c: send_content(u, c, "ass")))
dispatcher.add_handler(CommandHandler("real", send_real))
dispatcher.add_handler(CommandHandler("porno", send_porno))



@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    print("[DEBUG] Ricevuto POST da Telegram!")
    sys.stdout.flush()
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    print("[DEBUG] Richiesta GET ricevuta sulla /")
    sys.stdout.flush()
    return "NSFW Bot attivo."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
