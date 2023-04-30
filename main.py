import logging
from typing import Dict
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import os
PORT = int(os.environ.get('PORT', '8443'))
import prompts

import config as keys
from sqlite import SQLite
import time
from pathlib import Path
from langchain.llms import OpenAI
from langchain.chains import LLMChain

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
os.environ["OPENAI_API_KEY"] = keys.OPENAI_TOKEN

TOKEN = keys.TOKEN

db = SQLite('db.db')

here: Path = Path(__file__).parent
conversations: Path = here / "conversations"
conversations.mkdir(exist_ok=True)

isSearch = False

def welcome_message(update, context):
    data = context.bot.getChat(chat_id=update.effective_chat.id)
    if data is not None:
        (conversations / str(data.id)).mkdir(exist_ok=True)
        (
                conversations / str(data.id) / f"{int(time.time())}.ndjson"
        ).touch()
    update.message.reply_text('Hi, I am UA - EN Professional Translator. How can I help you? Print /help to get all commands.')


def start(update, context):
    update.message.reply_text('''
        Available commands:
/help - get the command list
/start_chat - chat with a translator
/translate - translate a word or text from Ukrainian to English
/saved - see your saved words list''')


def translate_cmd(update, context):
    update.message.reply_text('''
        To start translating simply type a word you want to translate. (:''')


def saved_list(update, context):
    data = context.bot.getChat(chat_id=update.effective_chat.id)
    user_id = data.id

    if db.saved_exists(user_id):
        saved = ""
        for row in db.select_saved(user_id):
            entry = str(row).replace("(", "").replace(",)", "")
            saved += ("\n" + entry)
        update.message.reply_text('Here is your Saved list: ')
        update.message.reply_text(saved)
    else:
        update.message.reply_text('Your Saved list is empty! Add some words first!')


def _translate(word_config: Dict = None, text_config: Dict = None) -> str:
    is_word = True if word_config else False
    temperature = 0 if is_word else 0.1
    llm = OpenAI(temperature=temperature)
    prompt = prompts.word
    args = {}
    if is_word:
        if word_config.get("syn", False):
            prompt = prompts.word_synonym
        elif word_config.get("syn_e", False):
            prompt = prompts.word_synonym_explenation
        elif word_config.get("trans", False):
            prompt = prompts.word_transcription
        args["word"] = word_config.get("word")
    else:
        args["text"] = text_config.get("text")
        if text_config.get("style", ""):
            prompt = prompts.text_style
            args["style"] = text_config.get("style")
        else:
            prompt = prompts.text
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(args)


def translate(update, context):
    update.message.reply_text('Please, wait a bit...')
    if update.message.from_user is not None and update.message.text is not None:
        text = update.message.text
        is_word = True if len(text.split(" ")) == 1 else False
        args = {
            "word_config": None if not is_word else { "word":  update.message.text },
            "text_config": None if is_word else { "text":  update.message.text }
        }
        response = _translate(**args)
        text_id = db.save_text(update.message.text)
        response_text_id = db.save_text(response)
        keyboard = [
            [InlineKeyboardButton("Synonyms", callback_data=f'tws{text_id}')],
            [InlineKeyboardButton("Synonyms with Explenations", callback_data=f'twes{text_id}')],
            [InlineKeyboardButton("Transcription", callback_data=f'tr{text_id}')],
            [InlineKeyboardButton("Save", callback_data=f'sv{text_id}|{response_text_id}')]
        ] if is_word else [
            [InlineKeyboardButton("Friendly", callback_data=f'st{text_id}|fr')],
            [InlineKeyboardButton("Formal", callback_data=f'st{text_id}|f')],
            [InlineKeyboardButton("Business", callback_data=f'st{text_id}|b')],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(response, reply_markup=markup)


def callback_inline(update, context):
    try:
        if update.callback_query.message:
            data = context.bot.getChat(chat_id=update.effective_chat.id)
            user_id = data.id
            if update.callback_query.data.startswith("tws"):
                word_id = update.callback_query.data.replace("tws", "")
                word = db.get_text(word_id)
                response = _translate(word_config={
                    "word": word,
                    "syn": True
                })
                update.callback_query.message.edit_text(response)
            elif update.callback_query.data.startswith("twes"):
                word_id = update.callback_query.data.replace("twes", "")
                word = db.get_text(word_id)
                response = _translate(word_config={
                    "word": word,
                    "syn_e": True
                })
                update.callback_query.message.edit_text(response)
            elif update.callback_query.data.startswith("tr"):
                word_id = update.callback_query.data.replace("tr", "")
                word = db.get_text(word_id)
                response = _translate(word_config={
                    "word": word,
                    "trans": True
                })
                update.callback_query.message.edit_text(response)
            elif update.callback_query.data.startswith("sv"):
                word_ids = update.callback_query.data.replace("sv", "").split("|")
                word1 = db.get_text(word_ids[0])
                word2 = db.get_text(word_ids[1])
                db.create_entry(user_id, f"{word1} - {word2}")
                update.callback_query.message.edit_text("The word was successfully added to your list.")
            elif update.callback_query.data.startswith("st"):
                sp = update.callback_query.data.replace("st", "").split("|")
                text = db.get_text(sp[0])
                style = "Formal"
                if sp[1] == "fr":
                    style = "Friendly"
                elif sp[1] == "b":
                    style = "Business"
                response = _translate(text_config={
                    "text": text,
                    "style": style
                })
                update.callback_query.message.edit_text(response)
    except Exception as e:
        print(f"Button didn't work: {e}")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", welcome_message))
    dp.add_handler(CommandHandler("start_chat", welcome_message))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("translate", translate_cmd))
    dp.add_handler(CommandHandler("saved", saved_list))

    dp.add_handler(CallbackQueryHandler(callback_inline, pattern='.*'))

    dp.add_handler(MessageHandler(Filters.text, translate))

    dp.add_error_handler(error)

    # updater.start_polling()

    updater.start_webhook(
       listen="0.0.0.0",
       port=int(PORT),
       url_path=TOKEN,
       webhook_url='https://bot-translate-dkuntso.herokuapp.com/' + TOKEN
    )

    updater.idle()

if __name__ == '__main__':
    main()
