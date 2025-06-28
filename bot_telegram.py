import os
import json
import threading
import time
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_eporner import fetch_eporner
from fetcher_audio import fetch_audio
from fetcher_manhwa import fetch_manhwa
from fetcher_redgifs import fetch_redgifs
from fetcher_e621 import fetch_e621
from fetcher_rule34video import fetch_rule34video

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

CACHE_FILES = {
    "hentai": "cache_hentai.json",
    "cosplay": "cache_cosplay.json",
    "real": "cache_real.json",
    "porno": "cache_porno.json",  # ora usa rule34video
    "manhwa": "cache_manhwa.json",
    "reddit_all": "cache_reddit.json",
    "gif": "cache_gif.json",
    "creampie": "cache_creampie.json",
    "facial": "cache_facial.json",
    "milf": "cache_milf.json",
    "ass": "cache_ass.json",
    "cosplayx": "cache_cosplayx.json",
    "facesitting": "cache_facesitting.json",
    "tightsfuck": "cache_tightsfuck.json",
    "posing": "cache_posing.json",
    "realhot": "cache_realhot.json",
    "rawass": "cache_rawass.json",
    "perfectcos": "cache_perfectcos.json",
    "redgifs": "cache_redgifs.json",
    "e621": "cache_e621.json",
    "rule34video": "cache_rule34video.json"
}

FAV_FILE = "favorites.json"
auto_threads = {}

def load_cache(mode):
    if mode not in CACHE_FILES:
        return set()
    file = CACHE_FILES[mode]
    if os.path.exists(file):
        with open(file, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(mode, cache):
    if mode not in CACHE_FILES:
        return
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

def is_banned(text):
    banned = ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl', 'gifv', 'svg', 'tiff']
    return any(bad in text.lower() for bad in banned)

def send_media(bot, chat_id, item):
    ext = item.get("ext", item['link'].split('.')[-1].lower())
    link = item['link']
    caption = f"{item['title'][:100]}\n🔗 {link}"
    if link.endswith('.gifv'):
        link = link.replace('.gifv', '.mp4')

    try:
        if ext in ['mp4', 'webm']:
            bot.send_video(chat_id=chat_id, video=link, caption=caption, timeout=60)
        elif ext in ['gif']:
            bot.send_animation(chat_id=chat_id, animation=link, caption=caption, timeout=30)
        elif ext in ['jpg', 'jpeg', 'png']:
            bot.send_photo(chat_id=chat_id, photo=link, caption=caption, timeout=30)
        else:
            bot.send_document(chat_id=chat_id, document=link, caption=caption, timeout=30)
    except Exception as e:
        print(f"[!] Errore media: {e}")
        bot.send_message(chat_id=chat_id, text=f"🔗 {caption}")

def send_only_video(update, context):
    chat_id = update.effective_chat.id
    sources = fetch_reddit(limit=50, sort="hot", target="realhot")
    sources += fetch_redgifs(limit=20)
    sources += fetch_eporner(limit=10)

    random.shuffle(sources)

    sent = 0
    for item in sources:
        if item['link'].lower().endswith(('.mp4', '.webm')):
            send_media(context.bot, chat_id, item)
            sent += 1
            if sent >= 5:
                break

    if sent == 0:
        context.bot.send_message(chat_id, "❌ Nessun video trovato.")


def load_channel_cache():
    if os.path.exists("cache_channel.json"):
        with open("cache_channel.json", "r") as f:
            return set(json.load(f))
    return set()

def save_channel_cache(cache):
    with open("cache_channel.json", "w") as f:
        json.dump(list(cache), f)

def send_to_channel(update: Update, context: CallbackContext, target=None):
    try:
        chat_id = update.effective_chat.id
        cache = load_channel_cache()
        sent = 0
        sources = []

        if target == "redgifs":
            sources = fetch_redgifs(limit=15)
        elif target == "nudegals":
            sources = fetch_nudegals(limit=10)
        elif target == "porno":
            sources = fetch_eporner(limit=10)
        elif target == "cosplay":
            sources = fetch_reddit(limit=10, target=target)
        elif target:
            sources = fetch_reddit(limit=30, target=target)
        else:
            sources = (
                fetch_redgifs(limit=10)
                + fetch_nudegals(limit=5)
                + fetch_reddit(limit=10, target="realhot")
                + fetch_reddit(limit=10, target="cosplayx")
            )

        random.shuffle(sources)

        for item in sources:
            item_id = f"{item['title']}_{item['link']}"
            if item_id in cache or is_banned(item_id):
                continue
            if not item['link'].lower().endswith(('.mp4', '.webm', '.gif', '.jpg', '.jpeg', '.png')):
                continue

            send_media(context.bot, CHANNEL_ID, item)
            cache.add(item_id)
            save_channel_cache(cache)
            sent += 1
            break

        if sent == 0:
            context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo da inviare al canale.")
        else:
            context.bot.send_message(chat_id=chat_id, text="✅ Contenuto inviato al canale.")

    except Exception as e:
        print(f"[!] Errore invio canale: {e}")
        context.bot.send_message(chat_id=chat_id, text="❌ Errore durante l'invio al canale.")



def send_content(update: Update, context: CallbackContext, mode="hentai"):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, f"📡 Cerco contenuti per /{mode}...")

    cache = load_cache(mode)
    results = []

    try:
        if mode in [
            "cosplay", "cosplayx", "gif", "creampie", "facial", "milf",
            "ass", "facesitting", "tightsfuck", "posing",
            "realhot", "rawass", "perfectcos", "reddit_all"
        ]:
            # Usa fetch_reddit migliorato con sort casuale (deciso dentro la funzione stessa)
            results += fetch_reddit(limit=100, target=mode)

        elif mode == "hentai":
            results += fetch_nhentai(limit=20)
            results += fetch_rule34(limit=20)

        elif mode == "porno":
            results += fetch_nudegals(limit=10)

        elif mode == "manhwa":
            results += fetch_manhwa(limit=20)

        else:
            context.bot.send_message(chat_id=chat_id, text="❌ Comando non valido.")
            return

        random.shuffle(results)
        sent = 0

        for item in results:
            item_id = f"{item['title']}_{item['link']}"
            if item_id in cache:
                continue
            if is_banned(item['title'] + item['link']):
                continue
            if not item['link'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm')):
                continue
            send_media(context.bot, chat_id, item)
            cache.add(item_id)
            sent += 1
            if sent >= 10:
                break

        save_cache(mode, cache)

        if sent == 0:
            context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")

    except Exception as e:
        import traceback
        print(f"\n[!] Errore in send_content({mode}):\n{traceback.format_exc()}\n")
        context.bot.send_message(chat_id=chat_id, text="⚠️ Errore nel caricamento contenuti.")

def reset_cache(update: Update, context: CallbackContext):
    for mode in CACHE_FILES:
        with open(CACHE_FILES[mode], "w") as f:
            json.dump([], f)
    update.message.reply_text("✅ Tutte le cache svuotate.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Benvenuto nel bot NSFW!\nComandi disponibili:\n\n"
        "/new\n/hentai\n/cosplay\n/real\n/porno\n/manhwa\n"
        "/gif /creampie /facial /milf /ass\n"
        "/cosplayx /facesitting /tightsfuck /posing /realhot /rawass /perfectcos\n"
        "/redgifs /e621 /rule34video\n"
        "/audio\n/fav <link>\n/favorites\n/random <tag>\n"
        "/loopon\n/loopoff\n/resetcache"
    )

def cmd_new(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, "🎁 Ecco una selezione mista per te...")
    for mode in ["hentai", "cosplay", "real", "porno", "reddit_all", "gif", "creampie", "facial", "milf", "ass", "cosplayx", "realhot"]:
        try:
            send_content(update, context, mode)
            time.sleep(2)
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
    for item in favs:
        send_media(context.bot, update.effective_chat.id, item)

def random_tag(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Esempio: /random creampie")
        return
    tag = context.args[0].lower()
    cache = load_cache("reddit_all")
    results = fetch_reddit(limit=50, sort="hot", target="reddit_all", tag=tag)
    for item in results:
        if tag not in item['title'].lower() or item['link'] in cache:
            continue
        send_media(context.bot, update.effective_chat.id, item)
        cache.add(item['link'])
        save_cache("reddit_all", cache)
        return
    update.message.reply_text("❌ Nessun risultato trovato.")

# ----- LOOP CONTROL -----
def auto_post_worker(chat_id, interval):
    while chat_id in auto_threads:
        try:
            # Puoi aggiungere altre fonti qui
            sources = fetch_reddit(limit=20, sort="hot", target="realhot")
            random.shuffle(sources)

            for item in sources:
                if item['link'].lower().endswith(('.mp4', '.webm', '.jpg', '.jpeg', '.png', '.gif')):
                    send_media(bot, chat_id, item)
                    break

        except Exception as e:
            print(f"[!] Errore auto-post: {e}")

        time.sleep(interval)

def start_auto_post(update, context):
    chat_id = update.effective_chat.id

    if chat_id in auto_threads and auto_threads[chat_id].is_alive():
        update.message.reply_text("⚠️ Auto-post già attivo.")
        return

    interval = 1800  # ogni 30 minuti (modificabile)
    thread = threading.Thread(target=auto_post_worker, args=(chat_id, interval), daemon=True)
    auto_threads[chat_id] = thread
    thread.start()

    update.message.reply_text(f"🔁 Auto-post attivato ogni {interval // 60} minuti.")

def stop_auto_post(update, context):
    chat_id = update.effective_chat.id

    if chat_id in auto_threads:
        del auto_threads[chat_id]
        update.message.reply_text("⛔ Auto-post disattivato.")
    else:
        update.message.reply_text("ℹ️ Nessun auto-post attivo per questo chat.")

# ----- DISPATCH -----

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("new", cmd_new))
dispatcher.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
dispatcher.add_handler(CommandHandler("cosplay", lambda u, c: send_content(u, c, "cosplay")))
dispatcher.add_handler(CommandHandler("real", lambda u, c: send_content(u, c, "real")))
dispatcher.add_handler(CommandHandler("porno", lambda u, c: send_content(u, c, "porno")))
dispatcher.add_handler(CommandHandler("manhwa", lambda u, c: send_content(u, c, "manhwa")))
dispatcher.add_handler(CommandHandler("reddit", lambda u, c: send_content(u, c, "reddit_all")))
dispatcher.add_handler(CommandHandler("gif", lambda u, c: send_content(u, c, "gif")))
dispatcher.add_handler(CommandHandler("creampie", lambda u, c: send_content(u, c, "creampie")))
dispatcher.add_handler(CommandHandler("facial", lambda u, c: send_content(u, c, "facial")))
dispatcher.add_handler(CommandHandler("milf", lambda u, c: send_content(u, c, "milf")))
dispatcher.add_handler(CommandHandler("ass", lambda u, c: send_content(u, c, "ass")))
dispatcher.add_handler(CommandHandler("cosplayx", lambda u, c: send_content(u, c, "cosplayx")))
dispatcher.add_handler(CommandHandler("facesitting", lambda u, c: send_content(u, c, "facesitting")))
dispatcher.add_handler(CommandHandler("tightsfuck", lambda u, c: send_content(u, c, "tightsfuck")))
dispatcher.add_handler(CommandHandler("posing", lambda u, c: send_content(u, c, "posing")))
dispatcher.add_handler(CommandHandler("realhot", lambda u, c: send_content(u, c, "realhot")))
dispatcher.add_handler(CommandHandler("rawass", lambda u, c: send_content(u, c, "rawass")))
dispatcher.add_handler(CommandHandler("perfectcos", lambda u, c: send_content(u, c, "perfectcos")))
dispatcher.add_handler(CommandHandler("audio", send_audio))
dispatcher.add_handler(CommandHandler("fav", add_fav))
dispatcher.add_handler(CommandHandler("favorites", list_fav))
dispatcher.add_handler(CommandHandler("random", random_tag))
dispatcher.add_handler(CommandHandler("autoposton", start_auto_post))
dispatcher.add_handler(CommandHandler("autopostoff", stop_auto_post))
dispatcher.add_handler(CommandHandler("resetcache", reset_cache))
dispatcher.add_handler(CommandHandler("redgifs", lambda u, c: send_content(u, c, "redgifs")))
dispatcher.add_handler(CommandHandler("e621", lambda u, c: send_content(u, c, "e621")))
dispatcher.add_handler(CommandHandler("rule34video", lambda u, c: send_content(u, c, "rule34video")))
dispatcher.add_handler(CommandHandler("video", send_only_video))


def get_channel_id(update: Update, context: CallbackContext):
    chat = update.effective_chat
    context.bot.send_message(
        chat.id,
        f"📡 Questo è il chat_id:\n<code>{chat.id}</code>",
        parse_mode="HTML"
    )
dispatcher.add_handler(CommandHandler("getid", get_channel_id))

def cmd_channel_push(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 Invio contenuto NSFW nel canale...")
    send_to_channel(context, target="realhot")
    
def send_channel_push(update: Update, context: CallbackContext):
    send_to_channel(update, context, random.choice(["redgifs", "nudegals", "cosplay"]))

dispatcher.add_handler(CommandHandler("channelpush", send_channel_push))
dispatcher.add_handler(CommandHandler("channelredgifs", lambda u, c: send_to_channel(u, c, "redgifs")))
dispatcher.add_handler(CommandHandler("channelnudegals", lambda u, c: send_to_channel(u, c, "nudegals")))


def auto_post_user_worker(chat_id, interval=1800):
    while True:
        try:
            sources = fetch_reddit(limit=20, sort="hot", target="realhot")
            random.shuffle(sources)
            for item in sources:
                if is_direct_video(item['link']):
                    send_media(bot, chat_id, item)
                    break
        except Exception as e:
            print(f"[!] Auto user post error: {e}")
        time.sleep(interval)


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "NSFW Bot attivo."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
