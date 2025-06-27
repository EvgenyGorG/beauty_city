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
    """Обработчик команды "Вернуться в главное меню"."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Что вас интересует?",
        reply_markup=build_keyboard('main_menu', menu_constants.MAIN_MENU)
    )


def handle_main_menu_appointment(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Выберите способ записи:",
        reply_markup=build_keyboard('appointment_type', menu_constants.APPOINTMENT_TYPE)
    )


def handle_appointment_type(update, context):
    query = update.callback_query
    query.answer()
    callback_data = query.data  # например: "appointment_type_0"

    if callback_data == 'appointment_type_0':
        context.user_data['booking'] = {'type': 'by_address'}
        query.edit_message_text(
            text="Вы выбрали запись по адресу. Выберите салон:",
            reply_markup=build_keyboard('choose_address', menu_constants.CHOOSE_ADDRESS)
        )
    elif callback_data == 'appointment_type_1':
        context.user_data['booking'] = {'type': 'by_master'}
        query.edit_message_text(
            text="Вы выбрали запись к любимому мастеру. Эта функция пока в разработке.",
            reply_markup=back_to_menu()
        )


def handle_choose_address(update, context):
    query = update.callback_query
    query.answer()
    callback_data = query.data  # например: choose_address_1

    # получаем индекс кнопки
    index = int(callback_data.split('_')[-1])
    address = menu_constants.CHOOSE_ADDRESS[index][0]

    # сохраняем в context
    if 'booking' not in context.user_data:
        context.user_data['booking'] = {}
    context.user_data['booking']['address'] = address

    query.edit_message_text(
        text=f"Вы выбрали: {address}\n\nТеперь выберите категорию услуги:",
        reply_markup=build_keyboard('choose_service_category', menu_constants.SERVICE_CATEGORIES)
    )


def handle_choose_master(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Пока выбор мастера в разработке. Выберите другой вариант или вернитесь в меню.",
        reply_markup=back_to_menu()
    )


def handle_manage_bookings(update, context): # меню где можно будет удалять уже имеющиеся записи, еще не сделано
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
    """Оставить отзыв."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Спасибо, что решили поделиться с нами обратной связью! '
             'Напишите, пожалуйста, своё сообщение — это может быть отзыв, идея или предложение.\n\n'
             'Если хотите, чтобы менеджер с вами связался, не забудьте об этом упомянуть 🌸'
    )
    context.user_data['waiting_feedback'] = True
