from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import menu_constants


def build_keyboard(action_type, button_rows):
    """Универсальная функция для создания меню из констант."""
    keyboard = [
        [InlineKeyboardButton(text=button_label, callback_data=f"{action_type}_{row_index}")]
        for row_index, [button_label] in enumerate(button_rows)
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu():
    """Кнопка для возвращения в главное меню."""
    keyboard = [[InlineKeyboardButton(text='⬅️ Вернуться в главное меню', callback_data='to_menu')]]
    return InlineKeyboardMarkup(keyboard)


def handle_back_to_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Что вас интересует?",
        reply_markup=build_keyboard('main_menu', menu_constants.MAIN_MENU)
    )


def handle_main_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Выберите салон:",
        reply_markup=build_keyboard('choose_address', menu_constants.CHOOSE_ADDRESS)
    )


def handle_booking(update, context): # меню записи, пока не сделано
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Выберите салон:",
        reply_markup=build_keyboard('choose_address', menu_constants.CHOOSE_ADDRESS)
    )


def handle_manage_bookings(update, context): # меню где можно будет удалять уже имеющиеся записи
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Здесь будет управление вашими записями"
    )


def handle_manager_contact(update, context):
    """Контакты менеджера салона."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Если у тебя есть вопросы или нужна помощь — наш менеджер всегда на связи: \n+7 (999) 000-11-22 \nНо для записи лучше воспользоваться ботом — это быстро, удобно и без ожиданий!\n Мы здесь, чтобы сделать твой опыт максимально лёгким и приятным 💖",
        reply_markup=back_to_menu()
    )


def handle_feedback(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Спасибо, что решили поделиться с нами обратной связью! '
             'Напишите, пожалуйста, своё сообщение — это может быть отзыв, идея или предложение.\n\n'
             'Если хотите, чтобы менеджер с вами связался, не забудьте об этом упомянуть 🌸'
    )
    context.user_data['waiting_feedback'] = True
