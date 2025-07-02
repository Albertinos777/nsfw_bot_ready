import os
import json
import threading
import time
import random
import asyncio
import telegram
from flask import Flask, request
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from fetcher_nhentai import fetch_nhentai
from fetcher_rule34 import fetch_rule34
from fetcher_reddit import fetch_reddit
from fetcher_eporner import fetch_eporner
from fetcher_manhwa import fetch_manhwa
from fetcher_redgifs import fetch_redgifs
from fetcher_e621 import fetch_e621
from fetcher_rule34video import fetch_rule34video

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

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
CHANNEL_CACHE_FILE = "cache_channel.json"
auto_threads = {}

# Cache helpers
def load_cache(mode):
    try:
        with open(CACHE_FILES.get(mode, ""), "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_cache(mode, cache):
    with open(CACHE_FILES.get(mode, ""), "w") as f:
        json.dump(list(cache), f)

def load_favorites():
    try:
        with open(FAV_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_favorite(item):
    favs = load_favorites()
    if item not in favs:
        favs.append(item)
        with open(FAV_FILE, "w") as f:
            json.dump(favs, f)

def load_channel_cache():
    try:
        with open(CHANNEL_CACHE_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_channel_cache(cache):
    with open(CHANNEL_CACHE_FILE, "w") as f:
        json.dump(list(cache), f)

def is_banned(text):
    banned = ["futanari", "yaoi", "gay", "trap", "dickgirl", "svg", "tiff"]
    return any(b in text.lower() for b in banned)

# Send content
async def send_media(context: ContextTypes.DEFAULT_TYPE, chat_id, item):
    link = item["link"]
    caption = f"{item['title'][:100]}\n🔗 {link}"

    try:
        if link.lower().endswith((".mp4", ".webm")):
            await context.bot.send_video(chat_id, link, caption=caption)
        elif link.lower().endswith((".gif")):
            await context.bot.send_animation(chat_id, link, caption=caption)
        elif link.lower().endswith((".jpg", ".jpeg", ".png")):
            await context.bot.send_photo(chat_id, link, caption=caption)
        else:
            await context.bot.send_document(chat_id, link, caption=caption)
    except Exception as e:
        await context.bot.send_message(chat_id, f"Errore invio: {e}")

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot NSFW pronto. Usa i comandi per ricevere contenuti.")

async def send_content(update: Update, context: ContextTypes.DEFAULT_TYPE, mode):
    await update.message.reply_text(f"Cerco contenuti per /{mode}...")

    results = []

    try:
        if mode == "hentai":
            results += fetch_nhentai(20)
            results += fetch_rule34(20)
        elif mode in ["cosplay", "cosplayx", "gif", "creampie", "facial", "milf", "ass", "facesitting", "tightsfuck", "posing", "realhot", "rawass", "perfectcos", "reddit_all"]:
            results += await fetch_reddit(limit=100, target=mode)
        elif mode == "real":
            results += await fetch_reddit(50, "realhot")
        elif mode == "porno":
            results += fetch_eporner(20)
        elif mode == "manhwa":
            results += fetch_manhwa(20)
        elif mode == "redgifs":
            results += fetch_redgifs(20)
        elif mode == "e621":
            results += fetch_e621(20)
        elif mode == "rule34video":
            results += fetch_rule34video(20)
        else:
            await update.message.reply_text("Comando non valido.")
            return
    except Exception as e:
        print(f"[!] Errore fetch contenuti: {e}")
        await update.message.reply_text("Errore durante la ricerca dei contenuti.")
        return

    random.shuffle(results)
    cache = load_cache(mode)
    sent = 0

    for item in results:
        try:
            item_id = f"{item['title']}_{item['link']}"
            if item_id in cache or is_banned(item['title'] + item['link']):
                continue

            ext = item["ext"].lower()
            link = item["link"]
            caption = item["title"]

            if ext in ["jpg", "jpeg", "png"]:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=link, caption=caption)
            elif ext == "gif":
                await context.bot.send_animation(chat_id=update.effective_chat.id, animation=link, caption=caption)
            elif ext in ["mp4", "webm"]:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=link, caption=caption)
            else:
                print(f"[DEBUG] Estensione non gestita: {ext}")
                continue

            cache.add(item_id)
            sent += 1

            if sent >= 10:
                break

        except Exception as e:
            print(f"[!] Errore invio media: {e}")

    save_cache(mode, cache)

    if sent == 0:
        await update.message.reply_text("Nessun nuovo contenuto trovato o tutti già inviati.")

async def add_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Devi fornire il link del contenuto.")
        return
    link = context.args[0]
    save_favorite({"title": "Preferito", "link": link, "thumb": link})
    await update.message.reply_text("Salvato nei preferiti!")

async def list_fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    favs = load_favorites()
    if not favs:
        await update.message.reply_text("Nessun contenuto nei preferiti.")
        return
    for item in favs:
        await send_media(context, update.effective_chat.id, item)

async def random_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Esempio: /random creampie")
        return

    tag = context.args[0].lower()

    if is_banned(tag):
        await update.message.reply_text("Tag non consentito.")
        return

    cache = load_cache("reddit_all")
    results = fetch_reddit(50, "reddit_all", tag=tag)

    for item in results:
        if tag not in item['title'].lower() or item['link'] in cache:
            continue
        await send_media(context, update.effective_chat.id, item)
        cache.add(item['link'])
        save_cache("reddit_all", cache)
        return

    await update.message.reply_text("Nessun risultato trovato.")

async def reset_cache(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for mode in CACHE_FILES:
        with open(CACHE_FILES[mode], "w") as f:
            json.dump([], f)
    await update.message.reply_text("Cache svuotate.")

async def send_video_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cerco video...")
    results = []
    results += fetch_reddit(50, "realhot")
    results += fetch_redgifs(20)
    results += fetch_eporner(10)
    valid = [i for i in results if i['link'].lower().endswith((".mp4", ".webm"))]

    if not valid:
        await update.message.reply_text("Nessun video trovato.")
        return

    random.shuffle(valid)
    for item in valid[:5]:
        await send_media(context, update.effective_chat.id, item)

async def auto_post_worker(chat_id, interval, application):
    while chat_id in auto_threads:
        try:
            results = []
            results += fetch_reddit(20, "realhot")
            results += fetch_reddit(20, "cosplayx")
            results += fetch_redgifs(20)
            results += fetch_eporner(10)
            random.shuffle(results)

            sent = 0
            for item in results:
                if is_banned(item['title'] + item['link']):
                    continue
                if item['link'].lower().endswith((".mp4", ".webm", ".jpg", ".jpeg", ".png", ".gif")):
                    await application.bot.send_message(chat_id, text=item['link'])
                    sent += 1
                if sent >= 10:
                    break
        except Exception as e:
            print(f"Errore auto-post: {e}")

        await asyncio.sleep(interval)

async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in auto_threads:
        await update.message.reply_text("Auto-post già attivo.")
        return

    loop = asyncio.get_event_loop()
    task = loop.create_task(auto_post_worker(chat_id, 900, context.application))
    auto_threads[chat_id] = task
    await update.message.reply_text("Auto-post attivato ogni 15 minuti.")

async def stop_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in auto_threads:
        auto_threads[chat_id].cancel()
        del auto_threads[chat_id]
        await update.message.reply_text("Auto-post disattivato.")
    else:
        await update.message.reply_text("Nessun auto-post attivo.")

@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(application.process_update(update))
    return "OK"



@app.route("/", methods=["GET"])
def index():
    return "Bot NSFW attivo."

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("hentai", lambda u, c: send_content(u, c, "hentai")))
application.add_handler(CommandHandler("cosplay", lambda u, c: send_content(u, c, "cosplay")))
application.add_handler(CommandHandler("real", lambda u, c: send_content(u, c, "real")))
application.add_handler(CommandHandler("porno", lambda u, c: send_content(u, c, "porno")))
application.add_handler(CommandHandler("manhwa", lambda u, c: send_content(u, c, "manhwa")))
application.add_handler(CommandHandler("redgifs", lambda u, c: send_content(u, c, "redgifs")))
application.add_handler(CommandHandler("e621", lambda u, c: send_content(u, c, "e621")))
application.add_handler(CommandHandler("rule34video", lambda u, c: send_content(u, c, "rule34video")))
application.add_handler(CommandHandler("reddit", lambda u, c: send_content(u, c, "reddit_all")))
application.add_handler(CommandHandler("gif", lambda u, c: send_content(u, c, "gif")))
application.add_handler(CommandHandler("creampie", lambda u, c: send_content(u, c, "creampie")))
application.add_handler(CommandHandler("facial", lambda u, c: send_content(u, c, "facial")))
application.add_handler(CommandHandler("milf", lambda u, c: send_content(u, c, "milf")))
application.add_handler(CommandHandler("ass", lambda u, c: send_content(u, c, "ass")))
application.add_handler(CommandHandler("cosplayx", lambda u, c: send_content(u, c, "cosplayx")))
application.add_handler(CommandHandler("facesitting", lambda u, c: send_content(u, c, "facesitting")))
application.add_handler(CommandHandler("tightsfuck", lambda u, c: send_content(u, c, "tightsfuck")))
application.add_handler(CommandHandler("posing", lambda u, c: send_content(u, c, "posing")))
application.add_handler(CommandHandler("realhot", lambda u, c: send_content(u, c, "realhot")))
application.add_handler(CommandHandler("rawass", lambda u, c: send_content(u, c, "rawass")))
application.add_handler(CommandHandler("perfectcos", lambda u, c: send_content(u, c, "perfectcos")))
application.add_handler(CommandHandler("video", send_video_pack))
application.add_handler(CommandHandler("autoposton", start_auto))
application.add_handler(CommandHandler("autopostoff", stop_auto))
application.add_handler(CommandHandler("fav", add_fav))
application.add_handler(CommandHandler("favorites", list_fav))
application.add_handler(CommandHandler("random", random_tag))
application.add_handler(CommandHandler("resetcache", reset_cache))

if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        print("[OK] Webhook impostato correttamente.")
        
        # Flask dentro al loop principale
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        
        config = Config()
        config.bind = ["0.0.0.0:10000"]
        
        print("[INFO] Avvio Flask + Hypercorn...")
        await serve(app, config)

    asyncio.run(main())
