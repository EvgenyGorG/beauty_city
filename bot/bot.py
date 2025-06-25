import os
# import django
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from bot_helper import build_keyboard
from menu_constants import MAIN_MENU


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beauty_city.settings")
# django.setup()
# from app.models import YourModel  # импорт моделей после настройки Django


def start(update, context):
    update.message.reply_text(
        "BeautyCity приветствует вас! Что вас интересует?",
        reply_markup=build_keyboard('main_menu', MAIN_MENU)
    )


def button_handler(update, context):
    query = update.callback_query
    query.answer()
    callback_id = query.data
    query.edit_message_text(text=f"Вы нажали кнопку с ID: {callback_id}")


def run_bot():
    load_dotenv()
    tg_token = os.environ['TG_TOKEN']

    updater = Updater(tg_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start)) # обработчик start
    dp.add_handler(CallbackQueryHandler(button_handler))  # обработчик кнопок

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()
