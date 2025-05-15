import os
import json
import threading
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_xvideos import fetch_xvideos

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

CACHE_FILES = {
    "hentai": "cache_hentai.json",
    "cosplay": "cache_cosplay.json",
    "real": "cache_real.json"
}

loop_enabled = {}

def load_cache(mode):
    file = CACHE_FILES[mode]
    if os.path.exists(file):
        with open(file, "r") as f:
            return set(json.load(f))
    return set()

def save_cache(mode, cache):
    with open(CACHE_FILES[mode], "w") as f:
        json.dump(list(cache), f)

def is_banned(title):
    banned = ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl']
    return any(bad in title.lower() for bad in banned)

def send_content(update: Update, context: CallbackContext, mode="hentai"):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, f"📡 Cerco nuovi contenuti per /{mode}...")

    cache = load_cache(mode)
    results = []

    if mode == "hentai":
        results += fetch_nhentai(limit=30)
        results += fetch_rule34(limit=30)
    elif mode == "cosplay":
        results += fetch_reddit(limit=30, sort="new")
    elif mode == "real":
        results += fetch_xvideos(limit=30)

    sent = 0
    for item in results:
        if item['link'] in cache or is_banned(item['title']):
            continue
        try:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=item['thumb'],
                caption=f"{item['title'][:100]}\n🔗 {item['link']}"
            )
            cache.add(item['link'])
            sent += 1
            if sent >= 10:
                break
        except Exception as e:
            print(f"[!] Errore invio: {e}")
            continue

    save_cache(mode, cache)

    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")
        
def send_reddit(update, context, mode="cosplay"):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, f"📡 Cerco contenuti Reddit ({mode})...")
    cache = load_cache(mode)
    results = fetch_reddit(limit=30, target=mode)

    sent = 0
    for item in results:
        if item['link'] in cache or is_banned(item['title']):
            continue
        try:
            ext = item.get("ext", "")
            if ext in ['gif', 'webm', 'mp4']:
                context.bot.send_video(chat_id=chat_id, video=item['link'], caption=f"{item['title']}")
            else:
                context.bot.send_photo(chat_id=chat_id, photo=item['thumb'], caption=f"{item['title']}")
            cache.add(item['link'])
            sent += 1
            if sent >= 10:
                break
        except Exception as e:
            print(f"[!] Reddit send error: {e}")
            continue

    save_cache(mode, cache)

    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto Reddit nuovo.")

def reset_cache(update: Update, context: CallbackContext):
    for mode in CACHE_FILES:
        with open(CACHE_FILES[mode], "w") as f:
            json.dump([], f)
    update.message.reply_text("✅ Tutte le cache svuotate.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Benvenuto. Comandi:\n/new\n/hentai\n/cosplay\n/real\n/resetcache\n/loopon\n/loopoff"
    )

def cmd_new(update: Update, context: CallbackContext):
    send_content(update, context, "hentai")
    send_content(update, context, "cosplay")
    send_content(update, context, "real")

# --- LOOP ---

def loop_worker(chat_id):
    while loop_enabled.get(chat_id, False):
        for mode in ["hentai", "cosplay", "real"]:
            try:
                cache = load_cache(mode)
                results = []
                if mode == "hentai":
                    results += fetch_nhentai(limit=10)
                    results += fetch_rule34(limit=10)
                elif mode == "cosplay":
                    results += fetch_reddit(limit=10, sort="new")
                elif mode == "real":
                    results += fetch_xvideos(limit=10)
                for item in results:
                    if item['link'] in cache or is_banned(item['title']):
                        continue
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=item['thumb'],
                        caption=f"{item['title'][:100]}\n🔗 {item['link']}"
                    )
                    cache.add(item['link'])
                    save_cache(mode, cache)
                    break
            except Exception as e:
                print(f"[!] Loop error: {e}")
        time.sleep(3600)  # ogni ora

def loop_on(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    loop_enabled[chat_id] = True
    update.message.reply_text("🔁 Loop automatico attivato (ogni ora).")
    threading.Thread(target=loop_worker, args=(chat_id,), daemon=True).start()

def loop_off(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    loop_enabled[chat_id] = False
    update.message.reply_text("⛔ Loop automatico disattivato.")

# --- TELEGRAM ROUTING ---

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("new", cmd_new))
dispatcher.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
dispatcher.add_handler(CommandHandler("cosplay", lambda u, c: send_reddit(u, c, "cosplay")))
dispatcher.add_handler(CommandHandler("real", lambda u, c: send_content(u, c, "real")))
dispatcher.add_handler(CommandHandler("resetcache", reset_cache))
dispatcher.add_handler(CommandHandler("loopon", loop_on))
dispatcher.add_handler(CommandHandler("loopoff", loop_off))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot NSFW attivo."

if __name__ == "__main__":
    print("✅ Bot pronto (Render webhook)")
    app.run(host="0.0.0.0", port=10000)
