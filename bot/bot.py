import os
from os import getenv

# import django
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot_utils import build_keyboard, handle_manager_contact, handle_back_to_menu, handle_feedback, back_to_menu
from menu_constants import MAIN_MENU


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_city.settings')
# django.setup()
# from app.models import YourModel  # импорт моделей после настройки Django

HANDLER_MAP = {
    'to_menu': handle_back_to_menu,
    'main_menu_0': '', # запись
    'main_menu_1': '', # управление (удаление) записей
    'main_menu_2': handle_manager_contact,
    'main_menu_3': handle_feedback
}


def start(update, context):
    """Обработчик команды /start."""
    update.message.reply_text(
        'BeautyCity приветствует вас! Что вас интересует?',
        reply_markup=build_keyboard('main_menu', MAIN_MENU)
    )


def button_handler(update, context):
    """Обработчик нажатий кнопок в меню."""
    query = update.callback_query
    query.answer()
    callback_id = query.data

    handler = HANDLER_MAP.get(callback_id)
    if handler:
        handler(update, context)
    else:
        query.edit_message_text('Ваш выбор не распознан. Пожалуйста, выберите действие из меню или нажмите /start, чтобы начать заново')


def message_handler(update, context):
    """Обработчик текстового сообщения."""
    if context.user_data.get('waiting_feedback'):
        context.user_data['waiting_feedback'] = False
        user = update.message.from_user
        feedback_text = update.message.text
        message = (
            f"📝 Новый отзыв от @{user.username or user.first_name} (id: {user.id}):\n\n"
            f"{feedback_text}"
        )

        context.bot.send_message(chat_id='@devmn_beauty_city_feedback', text=message)
        update.message.reply_text("Спасибо за ваш отзыв! 🌸", reply_markup=back_to_menu())
    else:
        update.message.reply_text("Пожалуйста, выберите действие из меню или нажмите /start.")


def run_bot():
    load_dotenv()
    tg_token = os.environ['TG_TOKEN']

    updater = Updater(tg_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start)) # обработчик start
    dp.add_handler(CallbackQueryHandler(button_handler))  # обработчик кнопок
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))  # обработчик сообщений

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()
