from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext
from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_xvideos import fetch_xvideos
import json
import os

TOKEN = "8085463291:AAHUAN0Jb_-RMdYrrxQFX2j62dcu5bLnQXQ"
HISTORY_FILE = "sent_history.json"

# Carica contenuti già inviati per evitare duplicati
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)

# Comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Benvenuto. Scrivi /new per ricevere contenuti NSFW.")

# Comando /new per mandare contenuti
def send_new(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    update.message.reply_text("📡 Cerco nuovi contenuti...")

    history = load_history()
    results = []
    results += fetch_nhentai(limit=10)
    results += fetch_rule34(limit=10)
    results += fetch_reddit(limit=10)
    results += fetch_xvideos(limit=10)

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
            if sent >= 5:
                break
        except Exception as e:
            print(f"[!] Errore invio: {e}")
            continue

    if sent == 0:
        context.bot.send_message(chat_id=chat_id, text="😐 Nessun contenuto nuovo trovato.")
    else:
        save_history(history)

# Main loop
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("new", send_new))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
