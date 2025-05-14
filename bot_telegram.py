import os
import json
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from telegram.ext import Updater
from flask import Flask, request
from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_xvideos import fetch_xvideos

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # es. https://nsfwbot.onrender.com

HISTORY_FILE = "sent_history.json"

app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=4, use_context=True)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)

def send_content(update: Update, context: CallbackContext, mode="all"):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, "📡 Cerco nuovi contenuti...")

    history = load_history()
    results = []

    if mode in ["all", "hentai"]:
        results += fetch_nhentai(limit=20)
        results += fetch_rule34(limit=20)
    if mode in ["all", "cosplay"]:
        results += fetch_reddit(limit=20, sort="new")
    if mode in ["all", "real"]:
        results += fetch_xvideos(limit=20)

    sent = 0
    for item in results:
        if item['link'] in history:
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
        except:
            continue

    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")
    else:
        save_history(history)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Benvenuto nel tuo bot NSFW. Usa /new, /hentai, /cosplay, /real")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("new", lambda u, c: send_content(u, c, "all")))
dispatcher.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
dispatcher.add_handler(CommandHandler("cosplay", lambda u, c: send_content(u, c, "cosplay")))
dispatcher.add_handler(CommandHandler("real", lambda u, c: send_content(u, c, "real")))
dispatcher.add_handler(CommandHandler("more", lambda u, c: send_content(u, c, "all")))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot NSFW attivo."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
