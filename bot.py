# bot.py (Versija 13.0 - Renginių pataisymai ir reklama)
import logging, datetime, time
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler)
import database as db

# --- KONFIGURACIJA (ČIA ĮRAŠYKITE NAUJO KANALO DUOMENIS) ---
CONFIG = {
    "BOT_TOKEN": "8143252727:AAEs6JDsZEHTksl0XCz2IFkxJ0PVy7lVZPQ",
    "ADMIN_IDS": [1085333518, 5318490031,6479255662],
    "MAIN_CHANNEL_ID":-1002871359485,  # <-- ĮRAŠYKITE NAUJO KANALO ID
    "TOPIC_IDS": {
        "skelbimai": 1,   # <-- ĮRAŠYKITE NAUJOS "skelbimai" TEMOS ID
        "graffiti": 14,      # <-- ĮRAŠYKITE NAUJOS "graffiti" TEMOS ID
        # "sarasas" temos nebereikia, nes sąrašas bus siunčiamas į pagrindinį kanalą
    },
    "HASHTAG_SCORES": {'#tag': 1, '#throw': 2, '#bomb': 3, '#piece': 5, '#train': 10}
}

# --- ROLĖS IR VERTIMAI ---
ROLES_LT = {"graffiti": "👑 Graffiti", "rezisierius": "🎬 Režisierius", "operatorius": "👀 Operatorius", "montuotojas": "✂️ Montuotojas", "skeiteris": "🛹 Skeiteris", "bmx": "🚲 BMX", "graf_dizainas": "🎨 Grafinis dizainas", "reperis": "🎤 Reperis", "mc": "🎙 MC", "dj": "🎧 DJ", "beatboxeris": "🥁 Beatboxeris", "beatmakeris": "🎚 Beatmakeris", "prodiuseris": "🎵 Prodiuseris", "tekstu_rasytojas": "🧠 Tekstų rašytojas", "bboy": "🌀 B-Boy", "bgirl": "🔄 B-Girl", "fotografas": "📸 Fotografas", "vaizdo_kurejas": "🎥 Vaizdo kūrėjas", "socialmedia": "📱 Social media", "promoteris": "📣 Promoteris", "merch_kurejas": "📦 Merch kūrėjas", "vedejas": "🎤 Vedėjas", "organizatorius": "📅 Organizatorius", "fan": "❤️ Klausytojas"}
ROLES_EN = {"graffiti": "👑 Graffiti", "director": "🎬 Director", "operator": "👀 Operator", "editor": "✂️ Editor", "skater": "🛹 Skater", "bmx": "🚲 BMX", "graphic_designer": "🎨 Graphic Designer", "rapper": "🎤 Rapper", "mc": "🎙 MC", "dj": "🎧 DJ", "beatboxer": "🥁 Beatboxer", "beatmaker": "🎚 Beatmaker", "producer": "🎵 Producer", "lyricist": "🧠 Lyricist", "bboy": "🌀 B-Boy", "bgirl": "🔄 B-Girl", "photographer": "📸 Photographer", "video_creator": "🎥 Video Creator", "socialmedia": "📱 Social media", "promoter": "📣 Promoter", "merch_creator": "📦 Merch Creator", "host": "🎤 Host", "organizer": "📅 Organizer", "fan": "❤️ Fan"}

TRANSLATIONS = {
    "lt": {
        "score_top": "🏆 Top Graffiti Writers\n",
        "cooldown_message": "⏳ Šią komandą galėsite naudoti vėl po {seconds} sekundžių.",
        "event_format_new": "Naudojimas: /addevent Pavadinimas, Data, Vieta, [neprivaloma nuoroda]\n(Taip pat prie komandos galite pridėti nuotrauką)",
        "submit_one_tag_only": "❌ Prie vieno darbo galima nurodyti tik vieną grotažymę (hashtag).",
        "help": ("📝 *Pagalbos meniu*\n\n👤 *Bendros komandos:*\n• /start – Pasirinkti kalbą ir rolę.\n• /list – Parodo visų narių sąrašą.\n• /eventai – Parodo artėjančių renginių sąrašą.\n• /top – Parodo pakvietimų TOP.\n• /myref – Gauk asmeninę pakvietimo nuorodą.\n\n👑 *Graffiti Lygos komandos:*\n• *Norėdami pateikti darbą, tiesiog atsiųskite botui nuotrauką su viena grotažyme (hashtag) prieraše, pvz., #tag, #throw, #bomb, #piece, #train.*\n• /score – Parodo graffiti taškų lentelę.\n\n🔒 *Adminų komandos:*\n• /post – Sukurti naują skelbimą kanale.\n• /addevent – Pridėti naują renginį.\n• /delevent <pavadinimas> - Ištrinti renginį.\n• /setpoll <vardai> – Nustatyti 'Gatvės Lygos' kandidatus.\n• /clearpoll - Išvalyti 'Gatvės Lygos' kandidatus.\n• /gatveslyga – Paleisti 'Gatvės Lygos' balsavimą."),
        "welcome": "Sveiki! Aš esu bendruomenės botas. Žemiau matote komandų sąrašą. Norėdami pradėti, pasirinkite savo rolę.", "role_prompt": "Pasirinkite savo rolę:", "role_saved": "✅ Rolė išsaugota.", "roles": ROLES_LT, "submit_only_pm": "❌ Darbus galima teikti tik asmeniniame pokalbyje su botu.", "submit_only_role": "❌ Darbus teikti gali tik vartotojai su 'Graffiti' role.", "submit_photo_required": "❌ Reikia atsiųsti nuotrauką kartu su viena grotažyme (pvz., #piece) jos aprašyme (caption).", "submit_received": "✅ Darbas gautas! Kai administratorius patvirtins – jis bus paskelbtas kanale ir taškai bus pridėti.", "submit_admin_autoapproved": "✅ Tavo, kaip admino, darbas patvirtintas automatiškai ir netrukus bus paskelbtas kanale.", "score_none": "Kol kas neturi jokių taškų.", "score_you": "📈 Tavo taškai: {points}", "myref_onlypm": "Ši komanda veikia tik privačiame pokalbyje su botu.", "event_saved": "✅ Renginys sėkmingai sukurtas!", "admin_only": "⛔️ Ši komanda prieinama tik administratoriams.", "no_events": "Šiuo metu suplanuotų renginių nėra.", "poll_format_new": "Naudojimas: /setpoll Vardas1, Vardas2, Vardas3", "poll_saved": "✅ Balsavimo kandidatai išsaugoti.", "poll_min_candidates": "❌ Reikia nurodyti bent du kandidatus.", "no_candidates": "Pirmiausia administratorius turi nustatyti kandidatus su /setpoll komanda.", "top_intro": "👥 Aktyviausi Kvietėjai:", "top_none": "Kol kas niekas nieko nepakvietė. Būk pirmas!", "group_private_only": "Ši komanda veikia tik privačiame pokalbyje arba grupėje (ne kanale).", "list_header": "👥 Bendruomenės narių sąrašas:", "list_empty": "Narių sąrašas kol kas tuščias.", "post_format": "Naudojimas: /post <tema> Jūsų tekstas (kartu su žinute prisekite nuotrauką). Galimos temos: skelbimai.", "work_approved_post": "✅ Naujas darbas patvirtintas!\nAutorius: @{username}\nGavo taškų: {points}",
        "conversation_cancel": "Veiksmas atšauktas.", "conversation_ask_post_details": "Gerai, kuriam skelbimų kanalo temą? Įveskite temos pavadinimą (pvz., skelbimai) ir po tarpo norimą tekstą.", "conversation_ask_photo": "Dabar atsiųskite nuotrauką, kurią norite pridėti. Jei nuotraukos nereikia, parašykite /skip", "conversation_post_success": "✅ Skelbimas sėkmingai išsiųstas!", "conversation_ask_event_details": "Gerai, įveskite renginio informaciją formatu: Pavadinimas, Data, Vieta, [nebūtina nuoroda]"
    },
    "en": {"roles": ROLES_EN, "score_top": "🏆 Top Graffiti Writers\n", "cooldown_message": "⏳ You can use this command again in {seconds} seconds.", "submit_one_tag_only": "❌ Only one hashtag is allowed per submission.", # ir kiti EN vertimai...
    }
}

# --- DEKORATORIUS APSAUGAI NUO SPAM ---
def cooldown(seconds=60):
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not update.effective_user: return
            user_id = update.effective_user.id
            if user_id in CONFIG['ADMIN_IDS']:
                return await func(update, context, *args, **kwargs)

            command_name = func.__name__
            last_used_key = f"last_used_{command_name}"
            
            last_used = context.user_data.get(last_used_key, 0)
            now = time.time()

            if now - last_used < seconds:
                remaining = int(seconds - (now - last_used))
                lang = get_lang(user_id)
                if update.message and update.message.chat.type != 'private':
                    try:
                        await context.bot.send_message(chat_id=user_id, text=TRANSLATIONS[lang]['cooldown_message'].format(seconds=remaining))
                    except Exception as e:
                        logging.warning(f"Could not send cooldown PM to {user_id}: {e}")
                elif update.message:
                    await update.message.reply_text(TRANSLATIONS[lang]['cooldown_message'].format(seconds=remaining))
                return
            
            context.user_data[last_used_key] = now
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator

# --- PAGALBINĖS FUNKCIJOS ---
submitted_cache = {}
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_lang(user_id):
    lang = db.get_user_language(user_id)
    return lang if lang in TRANSLATIONS else "lt"

def private_or_group(msg):
    return getattr(msg.chat, "type", "") in ['private', 'group', 'supergroup']

async def publish_approved_work(context: ContextTypes.DEFAULT_TYPE, user_id: int, points: int, photo_id: str):
    user_info = db.get_user_info(user_id)
    username = user_info.get('username', f"user{user_id}")
    lang = get_lang(user_id)
    caption = TRANSLATIONS[lang]['work_approved_post'].format(username=username, points=points)
    try:
        await context.bot.send_photo(chat_id=CONFIG['MAIN_CHANNEL_ID'], message_thread_id=CONFIG['TOPIC_IDS']['graffiti'], photo=photo_id, caption=caption)
    except Exception as e:
        logging.error(f"KLAIDA siunčiant nuotrauką į 'graffiti' temą: {e}")
        await context.bot.send_message(chat_id=CONFIG['ADMIN_IDS'][0], text=f"Nepavyko publikuoti darbo kanale. Klaida: {e}")

# --- POKALBIŲ BŪSENOS ---
(AWAIT_POST_DETAILS, AWAIT_POST_PHOTO, AWAIT_EVENT_DETAILS, AWAIT_EVENT_PHOTO) = range(4)

# --- /post POKALBIO VALDYMAS ---
async def post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']:
        await update.message.reply_text(TRANSLATIONS[lang]['admin_only'])
        return ConversationHandler.END
    await update.message.reply_text(TRANSLATIONS[lang]['conversation_ask_post_details'])
    return AWAIT_POST_DETAILS

async def post_receive_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update.effective_user.id)
    try:
        topic_key, text = update.message.text.split(' ', 1)
        if topic_key not in CONFIG['TOPIC_IDS']:
            await update.message.reply_text(f"Nurodyta tema '{topic_key}' neegzistuoja. Bandykite dar kartą.")
            return AWAIT_POST_DETAILS
        context.chat_data['post_details'] = {'topic_key': topic_key, 'text': text}
        await update.message.reply_text(TRANSLATIONS[lang]['conversation_ask_photo'])
        return AWAIT_POST_PHOTO
    except ValueError:
        await update.message.reply_text("Neteisingas formatas. Įveskite temos pavadinimą ir po tarpo - tekstą.")
        return AWAIT_POST_DETAILS

async def post_receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = context.chat_data.pop('post_details', None)
    photo_id = update.message.photo[-1].file_id
    thread_id = CONFIG['TOPIC_IDS'][details['topic_key']]
    try:
        await context.bot.send_photo(CONFIG['MAIN_CHANNEL_ID'], photo=photo_id, caption=details['text'], message_thread_id=thread_id)
        await update.message.reply_text(TRANSLATIONS[get_lang(update.effective_user.id)]['conversation_post_success'])
    except Exception as e:
        logging.error(f"KLAIDA siunčiant post'ą su foto: {e}")
        await update.message.reply_text(f"❌ Įvyko klaida siunčiant post'ą. Klaida: {e}")
    return ConversationHandler.END

async def post_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = context.chat_data.pop('post_details', None)
    thread_id = CONFIG['TOPIC_IDS'][details['topic_key']]
    try:
        await context.bot.send_message(CONFIG['MAIN_CHANNEL_ID'], text=details['text'], message_thread_id=thread_id)
        await update.message.reply_text(TRANSLATIONS[get_lang(update.effective_user.id)]['conversation_post_success'])
    except Exception as e:
        logging.error(f"KLAIDA siunčiant post'ą be foto: {e}")
        await update.message.reply_text(f"❌ Įvyko klaida siunčiant post'ą. Klaida: {e}")
    return ConversationHandler.END

# --- /addevent POKALBIO VALDYMAS ---
async def addevent_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']:
        await update.message.reply_text(TRANSLATIONS[lang]['admin_only'])
        return ConversationHandler.END
    await update.message.reply_text(TRANSLATIONS[lang]['conversation_ask_event_details'])
    return AWAIT_EVENT_DETAILS

async def addevent_receive_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update.effective_user.id)
    try:
        parts = [p.strip() for p in update.message.text.split(',')]
        name, date, place = parts[0], parts[1], parts[2]
        link = parts[3] if len(parts) > 3 else None
        context.chat_data['event_details'] = {'name': name, 'date': date, 'place': place, 'link': link}
        await update.message.reply_text(TRANSLATIONS[lang]['conversation_ask_photo'])
        return AWAIT_EVENT_PHOTO
    except IndexError:
        await update.message.reply_text("Neteisingas formatas. Įveskite Pavadinimą, Datą, Vietą, [nebūtina nuoroda]. Bandykite dar kartą.")
        return AWAIT_EVENT_DETAILS

async def addevent_receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = context.chat_data.pop('event_details', None)
    photo_id = update.message.photo[-1].file_id
    db.add_event(details['name'], details['date'], details['place'], photo_id=photo_id, link=details['link'])
    await update.message.reply_text(TRANSLATIONS[get_lang(update.effective_user.id)]['event_saved'])
    return ConversationHandler.END

async def addevent_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = context.chat_data.pop('event_details', None)
    db.add_event(details['name'], details['date'], details['place'], photo_id=None, link=details['link'])
    await update.message.reply_text(TRANSLATIONS[get_lang(update.effective_user.id)]['event_saved'])
    return ConversationHandler.END

async def conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = get_lang(update.effective_user.id)
    context.chat_data.clear()
    await update.message.reply_text(TRANSLATIONS[lang]['conversation_cancel'])
    return ConversationHandler.END

# --- KITOS KOMANDOS IR HANDLERIAI ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message.chat.type != 'private': await update.message.reply_text("Norėdami pradėti, parašykite man asmeniškai (PM)."); return
    db.add_or_update_user(user.id, user.username or f"user{user.id}")
    if context.args:
        try:
            referrer_id = int(context.args[0])
            if referrer_id != user.id: db.save_invite(user.id, referrer_id)
        except (ValueError, IndexError): pass
    user_id = user.id
    lang = get_lang(user_id)
    keyboard = [[InlineKeyboardButton("▶️ Pasirinkti/Keisti Rolę", callback_data='show_roles')]]
    await update.message.reply_text(text=TRANSLATIONS[lang]['help'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await start_command(update, context)

async def photo_submission_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; lang = get_lang(user.id)
    if update.message.chat.type != 'private': return
    if db.get_user_role(user.id) != 'graffiti': return
    if not update.message.caption: return
    
    tags_found = [tag for tag in update.message.caption.lower().split() if tag in CONFIG['HASHTAG_SCORES']]
    
    if len(tags_found) > 1:
        await update.message.reply_text(TRANSLATIONS[lang]['submit_one_tag_only']); return
    if len(tags_found) == 0: return
        
    points = CONFIG['HASHTAG_SCORES'][tags_found[0]]
    photo_id = update.message.photo[-1].file_id

    if user.id in CONFIG['ADMIN_IDS']:
        db.add_graffiti_score(user.id, points)
        await update.message.reply_text(TRANSLATIONS[lang]['submit_admin_autoapproved'])
        await publish_approved_work(context, user.id, points, photo_id)
        return

    reply = await update.message.reply_text(TRANSLATIONS[lang]['submit_received'])
    submitted_cache[reply.message_id] = {'user_id': user.id, 'points': points, 'photo_id': photo_id}
    for admin_id in CONFIG['ADMIN_IDS']:
        try:
            await context.bot.send_photo(admin_id, photo=photo_id, caption=f"Naujas darbas nuo @{user.username or user.id} ({points} taškai).", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Patvirtinti", callback_data=f"approve_{reply.message_id}"), InlineKeyboardButton("❌ Atmesti", callback_data=f"reject_{reply.message_id}")]]))
        except Exception as e: logging.error(f"KLAIDA siunčiant pranešimą adminui {admin_id}: {e}")

@cooldown()
async def list_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id)
    members = db.get_all_members()
    if not members: await update.message.reply_text(TRANSLATIONS[lang]["list_empty"]); return
    text = TRANSLATIONS[lang]['list_header'] + "\n\n"; by_role = {}
    for member in members:
        role = member.get('role')
        if not role: continue
        if role not in by_role: by_role[role] = []
        username = f"@{member['username']}" if member.get('username') else f"user_id: {member['user_id']}"
        by_role[role].append(username)
    for role_key, users in by_role.items():
        role_name = TRANSLATIONS[lang]['roles'].get(role_key, role_key.capitalize())
        text += f"*{role_name}*:\n" + "\n".join(f"• {user}" for user in users) + "\n\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def post_daily_list_job(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Vykdomas dieninis narių sąrašo skelbimas.")
    list_text = generate_members_list_text('lt')
    try:
        # PAKEITIMAS: Siunčiama į pagrindinį kanalą (be message_thread_id)
        await context.bot.send_message(chat_id=CONFIG['MAIN_CHANNEL_ID'], text=list_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e: logging.error(f"Nepavyko išsiųsti dieninio sąrašo: {e}")

async def post_daily_events_job(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Vykdomas dieninis renginių skelbimas.")
    events = db.get_events()
    if not events:
        logging.info("Renginių nėra, nieko nesiunčiama.")
        return
        
    text = "📅 **Artimiausi Renginiai** 📅\n"
    for event in events:
        text += f"\n📍 *{event['name']}*\n*Kada:* {event['date']}\n*Kur:* {event['place']}\n"
        if event.get('link'):
            text += f"*Nuoroda:* {event['link']}\n"
    try:
        # PAKEITIMAS: Siunčiama į pagrindinį kanalą (be message_thread_id)
        await context.bot.send_message(chat_id=CONFIG['MAIN_CHANNEL_ID'], text=text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Nepavyko išsiųsti dieninio renginių sąrašo: {e}")

async def post_ad_job(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Siunčiama reklama.")
    ad_text = """
Nemokami antradieniai BRONX Billiardo Klube exclusive HH community! 🎱

👉 1 val. biliardo nemokamai po žaidimo - įmeskite IG stories su BRONX
bronx.resos.com/booking

Tiesiog rinkis antradienį, parodyk story bare – viskas 🍻

Resos (https://bronx.resos.com/booking)
Book a table at BRONX
"""
    try:
        # PAKEITIMAS: Siunčiama į pagrindinį kanalą (be message_thread_id)
        await context.bot.send_message(chat_id=CONFIG['MAIN_CHANNEL_ID'], text=ad_text, disable_web_page_preview=False)
    except Exception as e:
        logging.error(f"Nepavyko išsiųsti reklamos: {e}")

async def delevent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']: await update.message.reply_text(TRANSLATIONS[lang]['admin_only']); return
    event_name = " ".join(context.args)
    if not event_name: await update.message.reply_text("Naudojimas: /delevent <Tikslus Renginio Pavadinimas>"); return
    if db.delete_event(event_name) > 0: await update.message.reply_text(f"✅ Renginys '{event_name}' sėkmingai ištrintas.")
    else: await update.message.reply_text(f"❌ Renginys pavadinimu '{event_name}' nerastas.")

@cooldown()
async def eventai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id); events = db.get_events()
    if not events: await update.message.reply_text(TRANSLATIONS[lang]["no_events"]); return
    await update.message.reply_text("📅 Artimiausi renginiai:")
    for event in events:
        text = f"📍 *{event['name']}*\n*Kada:* {event['date']}\n*Kur:* {event['place']}"
        photo_id = event.get('photo_id')
        link = event.get('link')
        try:
            if photo_id:
                # Jei yra nuotrauka, siunčiame ją su aprašymu
                await update.message.reply_photo(photo=photo_id, caption=text, parse_mode=ParseMode.MARKDOWN)
                if link:
                    # Jei yra ir nuoroda, siunčiame ją atskirai
                    await update.message.reply_text(f"*Papildoma nuoroda:*\n{link}", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            elif link:
                # Jei yra tik nuoroda
                text += f"\n*Nuoroda:* {link}"
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            else:
                # Jei nieko nėra
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Failed to send event message: {e}")
            await update.message.reply_text(text + "\n(Nepavyko įkelti priedo)", parse_mode=ParseMode.MARKDOWN)

async def setpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']: await update.message.reply_text(TRANSLATIONS[lang]['admin_only']); return
    text = " ".join(context.args)
    if not text: await update.message.reply_text(TRANSLATIONS[lang]["poll_format_new"]); return
    candidates = [opt.strip() for opt in text.split(',') if opt.strip()]
    if len(candidates) < 2: await update.message.reply_text(TRANSLATIONS[lang]["poll_min_candidates"]); return
    db.save_pollglyga("|".join(candidates)); await update.message.reply_text(TRANSLATIONS[lang]['poll_saved'])

async def clearpoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']: await update.message.reply_text(TRANSLATIONS[lang]['admin_only']); return
    db.clear_poll(); await update.message.reply_text("✅ 'Gatvės Lygos' kandidatų sąrašas išvalytas.")

async def gatveslyga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']: await update.message.reply_text(TRANSLATIONS[lang]['admin_only']); return
    if not private_or_group(update.message): await update.message.reply_text(TRANSLATIONS[lang]['group_private_only']); return
    candidates_str = db.get_pollglyga()
    if not candidates_str: await update.message.reply_text(TRANSLATIONS[lang]['no_candidates']); return
    options = [opt.strip() for opt in candidates_str.split('|')]
    keyboard = [[InlineKeyboardButton("✅ Taip, paleisti", callback_data='confirm_poll_launch'), InlineKeyboardButton("❌ Atšaukti", callback_data='cancel_poll_launch')]]
    await update.message.reply_text(f"Kandidatai: *{', '.join(options)}*.\n\nAr tikrai norite paleisti balsavimą?", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

@cooldown()
async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id); top = db.get_top_graffiti(); personal = db.get_user_score(user_id)
    msg = TRANSLATIONS[lang]['score_top']
    if not top: msg += "\nKol kas niekas neturi taškų."
    else:
        for i, row in enumerate(top, 1): msg += f"\n{i}. @{row['username']} – {row['points']} tšk."
    msg += "\n\n" + (TRANSLATIONS[lang]['score_you'].format(points=personal) if personal else TRANSLATIONS[lang]['score_none'])
    await update.message.reply_text(msg)

@cooldown()
async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id); board = db.get_invite_leaderboard()
    msg = TRANSLATIONS[lang]["top_intro"] + "\n\n"
    if not board: msg += TRANSLATIONS[lang]["top_none"]
    else:
        for i, entry in enumerate(board, start=1): msg += f"{i}. @{entry['username']} – {entry['count']} pakviestų\n"
    await update.message.reply_text(msg)

@cooldown()
async def myref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id)
    if update.message.chat.type != "private": await update.message.reply_text(TRANSLATIONS[lang]["myref_onlypm"]); return
    user_id = update.effective_user.id; bot_username = (await context.bot.get_me()).username
    await update.message.reply_text(f"Tavo asmeninė pakvietimo nuoroda:\nhttps://t.me/{bot_username}?start={user_id}")
    
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in CONFIG['ADMIN_IDS']: return
    chat_id = update.message.chat.id
    thread_id = update.message.message_thread_id if update.message.is_topic_message else "Nėra (ne temos žinutė)"
    text = f"ℹ️ Informacija administratoriui:\nKanalo/Grupės ID: `{chat_id}`\nTemos ID: `{thread_id}`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def test_ad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; lang = get_lang(user_id)
    if user_id not in CONFIG['ADMIN_IDS']: await update.message.reply_text(TRANSLATIONS[lang]['admin_only']); return
    logging.info(f"Adminas {user_id} iškvietė testinę reklamos komandą.")
    await update.message.reply_text("✅ Siunčiama testinė reklama į pagrindinį kanalą...")
    await post_ad_job(context)

# --- MYGTUKŲ APDOROJIMAS ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; user_id = query.from_user.id; lang = get_lang(user_id); await query.answer()
    if query.data == 'show_roles':
        roles = TRANSLATIONS[lang]['roles']
        keyboard, row = [], []
        for i, (key, name) in enumerate(roles.items(), 1):
            row.append(InlineKeyboardButton(name, callback_data=f"role_{key}"))
            if i % 3 == 0: keyboard.append(row); row = []
        if row: keyboard.append(row)
        await query.message.reply_text(TRANSLATIONS[lang]['role_prompt'], reply_markup=InlineKeyboardMarkup(keyboard))
        try: await query.message.delete()
        except: pass
    elif query.data.startswith("role_"):
        role = query.data.split("_", 1)[1]
        db.update_user_data(user_id, 'role', role)
        await query.edit_message_text(TRANSLATIONS[lang]['role_saved'])
    elif query.data == 'confirm_poll_launch':
        if query.from_user.id not in CONFIG['ADMIN_IDS']: await query.answer("Šis veiksmas skirtas tik adminams.", show_alert=True); return
        candidates_str = db.get_pollglyga()
        if not candidates_str: await query.edit_message_text("Kandidatų sąrašas tuščias."); return
        options = [opt.strip() for opt in candidates_str.split('|')]
        await context.bot.send_poll(chat_id=query.message.chat_id, question="📢 GATVĖS LYGA: Išrinkite nugalėtoją!", options=options, is_anonymous=False, allows_multiple_answers=True)
        await query.edit_message_text("✅ Balsavimas paleistas.")
    elif query.data == 'cancel_poll_launch':
        await query.edit_message_text("Balsavimas atšauktas.")

async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; data = query.data; await query.answer()
    action, msg_id_str = data.split("_"); msg_id = int(msg_id_str)
    if msg_id not in submitted_cache:
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n(❌ Jau apdorota arba neberasta.)"); return
    sub = submitted_cache.pop(msg_id)
    if action == "approve":
        db.add_graffiti_score(sub['user_id'], sub['points'])
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n(✅ Patvirtinta. Skelbiama kanale.)")
        await publish_approved_work(context, sub['user_id'], sub['points'], sub['photo_id'])
    else:
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n(❌ Atmesta)")

# --- MAIN FUNKCIJA ---
def main():
    db.setup_database()
    app = Application.builder().token(CONFIG["BOT_TOKEN"]).build()

    post_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("post", post_start)],
        states={
            AWAIT_POST_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, post_receive_details)],
            AWAIT_POST_PHOTO: [MessageHandler(filters.PHOTO, post_receive_photo), CommandHandler("skip", post_skip_photo)],
        },
        fallbacks=[CommandHandler("cancel", conversation_cancel)],
    )
    addevent_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addevent", addevent_start)],
        states={
            AWAIT_EVENT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, addevent_receive_details)],
            AWAIT_EVENT_PHOTO: [MessageHandler(filters.PHOTO, addevent_receive_photo), CommandHandler("skip", addevent_skip_photo)],
        },
        fallbacks=[CommandHandler("cancel", conversation_cancel)],
    )
    app.add_handler(post_conv_handler)
    app.add_handler(addevent_conv_handler)
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_members_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("myref", myref_command))
    app.add_handler(CommandHandler("delevent", delevent_command))
    app.add_handler(CommandHandler("eventai", eventai_command))
    app.add_handler(CommandHandler("setpoll", setpoll_command))
    app.add_handler(CommandHandler("clearpoll", clearpoll_command))
    app.add_handler(CommandHandler("gatveslyga", gatveslyga_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("testad", test_ad_command))
    
    app.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, photo_submission_handler))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(show_roles|role_|confirm_poll_launch|cancel_poll_launch)"))
    app.add_handler(CallbackQueryHandler(admin_decision_handler, pattern="^(approve_|reject_)"))

    # Automatiniai darbai
    job_queue = app.job_queue
    # Laikai nurodyti UTC. Lietuvos laiku bus +3 valandos (vasarą).
    job_queue.run_daily(post_daily_list_job, time=datetime.time(hour=9, minute=0)) # 12:00 Lietuvos laiku
    job_queue.run_daily(post_daily_events_job, time=datetime.time(hour=10, minute=0)) # 13:00 Lietuvos laiku
    
    job_queue.run_daily(post_ad_job, time=datetime.time(hour=7, minute=0)) # 10:00 Lietuvos laiku
    job_queue.run_daily(post_ad_job, time=datetime.time(hour=12, minute=0)) # 15:00 Lietuvos laiku
    job_queue.run_daily(post_ad_job, time=datetime.time(hour=17, minute=0)) # 20:00 Lietuvos laiku
    
    logging.info("Botas paleidžiamas...")
    app.run_polling()

if __name__ == '__main__':
    main()