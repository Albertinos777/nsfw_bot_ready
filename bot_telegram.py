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
from fetcher_hqporner import fetch_hqporner
from fetcher_audio import fetch_audio
from fetcher_manhwa import fetch_manhwa  # Assicurati che esista

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

CACHE_FILES = {
    "hentai": "cache_hentai.json",
    "cosplay": "cache_cosplay.json",
    "real": "cache_real.json",
    "porno": "cache_porno.json",
    "manhwa": "cache_manhwa.json",
    "reddit_all": "cache_reddit.json",
    "gif": "cache_gif.json",
    "creampie": "cache_creampie.json",
    "facial": "cache_facial.json",
    "milf": "cache_milf.json",
    "ass": "cache_ass.json"
}

FAV_FILE = "favorites.json"
loop_enabled = {}  # chat_id: True/False

# 🔧 Reset globale all'avvio
loop_enabled.clear()
print("[BOOT] Loop disattivato all'avvio.")

# -------- UTIL --------

def load_cache(mode):
    file = CACHE_FILES.get(mode)
    if file and os.path.exists(file):
        with open(file, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(mode, cache):
    file = CACHE_FILES.get(mode)
    if file:
        with open(file, "w") as f:
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
    return any(b in text.lower() for b in banned)

def send_media(bot, chat_id, item):
    ext = item.get("ext", item['link'].split('.')[-1].lower())
    caption = f"{item['title'][:100]}\n🔗 {item['link']}"
    try:
        if ext in ['mp4', 'webm']:
            bot.send_video(chat_id=chat_id, video=item['link'], caption=caption, timeout=60)
        elif ext == 'gif':
            bot.send_animation(chat_id=chat_id, animation=item['link'], caption=caption, timeout=60)
        elif ext in ['jpg', 'jpeg', 'png']:
            bot.send_photo(chat_id=chat_id, photo=item['link'], caption=caption, timeout=60)
        else:
            bot.send_document(chat_id=chat_id, document=item['link'], caption=caption, timeout=60)
    except Exception as e:
        print(f"[!] Errore invio media: {e}")
        bot.send_message(chat_id=chat_id, text=caption)

# -------- CONTENUTI --------

def send_content(update: Update, context: CallbackContext, mode="hentai"):
    chat_id = update.effective_chat.id
    print(f"[DEBUG] Entrato in send_content({mode}) per chat {chat_id}")
    context.bot.send_message(chat_id, f"📡 Cerco contenuti per /{mode}...")

    cache = load_cache(mode)
    results = []

    try:
        if mode == "hentai":
            results += fetch_nhentai(limit=20)
            results += fetch_rule34(limit=20)
        elif mode == "cosplay":
            results += fetch_reddit(limit=25, sort="new", target="cosplay")
        elif mode == "real":
            results += fetch_reddit(limit=25, sort="top", target="reddit_all")
        elif mode == "porno":
            results += fetch_hqporner(limit=10)
        elif mode == "manhwa":
            results += fetch_manhwa(limit=10)
        elif mode in CACHE_FILES:
            results += fetch_reddit(limit=25, sort=random.choice(["hot", "top", "new"]), target="reddit_all")
        else:
            context.bot.send_message(chat_id, "❌ Comando non valido.")
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
            context.bot.send_message(chat_id, "😐 Nessun contenuto nuovo trovato.")

    except Exception as e:
        print(f"[!] Errore send_content({mode}): {e}")
        context.bot.send_message(chat_id, "⚠️ Errore nel caricamento contenuti.")

def cmd_new(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, "🎁 Ecco una selezione mista per te...")
    for mode in ["hentai", "cosplay", "real", "reddit_all", "gif", "creampie", "facial", "milf", "ass", "porno", "manhwa"]:
        try:
            send_content(update, context, mode)
            time.sleep(1)
        except Exception as e:
            print(f"[!] Errore in /new per {mode}: {e}")

def reset_cache(update: Update, context: CallbackContext):
    for mode in CACHE_FILES:
        save_cache(mode, set())
    update.message.reply_text("✅ Cache svuotate.")

def loop_worker(chat_id):
    print(f"[LOOP] Avviato per chat {chat_id}")
    while loop_enabled.get(chat_id, False):
        for mode in ["hentai", "cosplay", "real", "reddit_all"]:
            if not loop_enabled.get(chat_id, False):
                break
            try:
                cache = load_cache(mode)
                results = []
                if mode == "hentai":
                    results += fetch_nhentai(limit=5)
                    results += fetch_rule34(limit=5)
                elif mode == "cosplay":
                    results += fetch_reddit(limit=5, sort="new", target="cosplay")
                elif mode == "real":
                    results += fetch_reddit(limit=5, sort="hot", target="reddit_all")
                elif mode == "reddit_all":
                    results += fetch_reddit(limit=5, sort="top", target="reddit_all")

                for item in results:
                    if item['link'] in cache or is_banned(item['title'] + item['link']):
                        continue
                    send_media(bot, chat_id, item)
                    cache.add(item['link'])
                    save_cache(mode, cache)
                    break

            except Exception as e:
                print(f"[!] Errore nel loop: {e}")
        time.sleep(3600)

def loop_on(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if loop_enabled.get(chat_id, False):
        update.message.reply_text("⚠️ Il loop è già attivo.")
        return
    loop_enabled[chat_id] = True
    update.message.reply_text("🔁 Loop automatico attivato.")
    threading.Thread(target=loop_worker, args=(chat_id,), daemon=True).start()

def loop_off(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    loop_enabled[chat_id] = False
    update.message.reply_text("⛔ Loop disattivato.")

def loop_status(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    status = loop_enabled.get(chat_id, False)
    update.message.reply_text(f"📡 Loop attivo: {'✅ Sì' if status else '❌ No'}")

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
        update.message.reply_text("❌ Devi fornire il link.")
        return
    link = args[0]
    save_favorite({"title": "Preferito", "link": link, "thumb": link})
    update.message.reply_text("⭐️ Salvato nei preferiti.")

def list_fav(update: Update, context: CallbackContext):
    favs = load_favorites()
    if not favs:
        update.message.reply_text("📭 Nessun contenuto nei preferiti.")
        return
    for item in favs[-10:]:
        send_media(context.bot, update.effective_chat.id, item)

# -------- ROUTES --------

dispatcher.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Bot NSFW attivo.")))
dispatcher.add_handler(CommandHandler("new", cmd_new))
dispatcher.add_handler(CommandHandler("resetcache", reset_cache))
dispatcher.add_handler(CommandHandler("loopon", loop_on))
dispatcher.add_handler(CommandHandler("loopoff", loop_off))
dispatcher.add_handler(CommandHandler("loopstatus", loop_status))
dispatcher.add_handler(CommandHandler("audio", send_audio))
dispatcher.add_handler(CommandHandler("fav", add_fav))
dispatcher.add_handler(CommandHandler("favorites", list_fav))

# Dinamici
for cmd in CACHE_FILES:
    dispatcher.add_handler(CommandHandler(cmd, lambda u, c, m=cmd: send_content(u, c, m)))

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
