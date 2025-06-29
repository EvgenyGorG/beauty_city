import os
from os import getenv

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import bot_utils
from menu_constants import MAIN_MENU

HANDLER_MAP = {
    'to_menu': bot_utils.handle_back_to_menu,
    'main_menu': bot_utils.handle_main_menu,
    'appointment_type': bot_utils.handle_appointment_type,
    'choose_address': bot_utils.handle_choose_address,
    'choose_service_category': bot_utils.handle_choose_service_category,
    'choose_service': bot_utils.handle_concrete_service,
    'choose_master': bot_utils.handle_choose_master,
    'choose_service_after_master': bot_utils.handle_choose_service_after_master,
    'choose_date': bot_utils.handle_choose_date,
    'choose_time': bot_utils.handle_choose_time,
    'ask_name': bot_utils.handle_ask_name,
    'ask_phone': bot_utils.handle_ask_phone,
    'confirm_booking': bot_utils.handle_confirm_booking,
    'cancel_booking': bot_utils.handle_cancel_booking,
    'manage_bookings': bot_utils.handle_manage_bookings,
    'manager_contact': bot_utils.handle_manager_contact,
    'feedback': bot_utils.handle_feedback,
}


def start(update, context):
    """Обработчик команды /start."""
    update.message.reply_text(
        'BeautyCity приветствует вас! Что вас интересует?',
        reply_markup=bot_utils.build_keyboard('main_menu', MAIN_MENU)
    )


def button_handler(update, context):
    query = update.callback_query
    query.answer()
    data = query.data.strip()

    if data in HANDLER_MAP:
        action = data
        param = None
    else:
        if '_' in data:
            action, param = data.rsplit('_', 1)
        else:
            # На всякий случай, если вообще непонятно
            action = data
            param = None
    handler = HANDLER_MAP.get(action)
    if handler:
        handler(update, context, param)
    else:
        query.edit_message_text('Выбор не распознан, нажмите /start для начала.')


def message_handler(update, context):
    """Обработчик текстового сообщения."""
    current_step = context.user_data.get('current_step')

    if current_step and current_step in HANDLER_MAP:
        HANDLER_MAP[current_step](update, context)
        return

    if context.user_data.get('waiting_feedback'):
        context.user_data['waiting_feedback'] = False
        user = update.message.from_user
        feedback_text = update.message.text
        message = (
            f"📝 Новый отзыв от @{user.username or user.first_name} (id: {user.id}):\n\n"
            f"{feedback_text}"
        )

        context.bot.send_message(chat_id='@devmn_beauty_city_feedback', text=message)
        update.message.reply_text("Спасибо за ваш отзыв! 🌸", reply_markup=bot_utils.back_to_menu())
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
