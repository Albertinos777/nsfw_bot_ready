import os
import json
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

HISTORY_FILE = "sent_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)

def is_banned(title):
    banned = ['futanari', 'yaoi', 'gay', 'trap', 'dickgirl']
    return any(bad in title.lower() for bad in banned)

def send_content(update: Update, context: CallbackContext, mode="all"):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, "📡 Cerco nuovi contenuti...")

    history = load_history()
    results = []

    if mode in ["all", "hentai"]:
        results += fetch_nhentai(limit=30)
        results += fetch_rule34(limit=30)
    if mode in ["all", "cosplay"]:
        results += fetch_reddit(limit=30, sort="new")
    if mode in ["all", "real"]:
        results += fetch_xvideos(limit=30)

    sent = 0
    for item in results:
        if item['link'] in history or is_banned(item['title']):
            continue
        try:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=item['thumb'],
                caption=f"{item['title'][:100]}\n🔗 {item['link']}"
            )
            history.add(item['link'])
            sent += 1
            if sent >= 30:
                break
        except Exception as e:
            print(f"[!] Errore invio: {e}")
            continue

    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")
    else:
        save_history(history)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Benvenuto. Comandi: /new /cosplay /hentai /real /resetcache")

def reset_cache(update: Update, context: CallbackContext):
    with open("sent_history.json", "w") as f:
        json.dump([], f)
    update.message.reply_text("✅ Cache svuotata.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("new", lambda u, c: send_content(u, c, "all")))
dispatcher.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
dispatcher.add_handler(CommandHandler("cosplay", lambda u, c: send_content(u, c, "cosplay")))
dispatcher.add_handler(CommandHandler("real", lambda u, c: send_content(u, c, "real")))
dispatcher.add_handler(CommandHandler("resetcache", reset_cache))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot NSFW attivo."

if __name__ == "__main__":
    print("Avvio bot... (webhook impostato solo manualmente)")
    app.run(host="0.0.0.0", port=10000)
