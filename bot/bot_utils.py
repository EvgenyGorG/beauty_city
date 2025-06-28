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


def handle_back_to_menu(update, context, param=None):
    """Обработчик команды "Вернуться в главное меню"."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Что вас интересует?",
        reply_markup=build_keyboard('main_menu', menu_constants.MAIN_MENU)
    )


def handle_main_menu(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param == '0':
        query.edit_message_text(
            text="Выберите способ записи:",
            reply_markup=build_keyboard('appointment_type', menu_constants.APPOINTMENT_TYPE)
        )
    elif param == '1':
        handle_manage_bookings(update, context)
    elif param == '2':
        handle_manager_contact(update, context)
    elif param == '3':
        handle_feedback(update, context)
    else:
        query.edit_message_text(
            text="Что вас интересует?",
            reply_markup=build_keyboard('main_menu', menu_constants.MAIN_MENU)
        )


def handle_appointment_type(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param == '0':
        context.user_data['booking'] = {'type': 'by_address'}
        query.edit_message_text(
            text="Вы выбрали запись по адресу. Выберите салон:",
            reply_markup=build_keyboard('choose_address', menu_constants.CHOOSE_ADDRESS)
        )
    elif param == '1':
        context.user_data['booking'] = {'type': 'by_master'}
        query.edit_message_text(
            text="Вы выбрали запись к любимому мастеру. Эта функция пока в разработке.",
            reply_markup=back_to_menu()
        )
    else:
        query.edit_message_text("Неверный выбор. Попробуйте снова.", reply_markup=back_to_menu())


def handle_choose_address(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param is None:
        query.edit_message_text("Ошибка выбора адреса. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    address = menu_constants.CHOOSE_ADDRESS[index][0]

    if 'booking' not in context.user_data:
        context.user_data['booking'] = {}
    context.user_data['booking']['address'] = address

    query.edit_message_text(
        text=f"Вы выбрали: {address}\n\nТеперь выберите категорию услуги:",
        reply_markup=build_keyboard('choose_service_category', menu_constants.SERVICE_CATEGORIES)
    )


def handle_choose_service_category(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param is None:
        query.edit_message_text("Ошибка выбора категории услуги. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    service_category = menu_constants.SERVICE_CATEGORIES[index][0]

    if 'booking' not in context.user_data:
        context.user_data['booking'] = {}
    context.user_data['booking']['service_category'] = service_category

    query.edit_message_text(
        text=f"Вы выбрали категорию услуги: {service_category}\n\nСпасибо за выбор! Скоро с вами свяжутся.",
        reply_markup=back_to_menu()
    )


def handle_manage_bookings(update, context, param=None):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Здесь будет управление вашими записями"
    )


def handle_manager_contact(update, context, param=None):
    """Контакты менеджера салона."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Если у тебя есть вопросы или нужна помощь — наш менеджер всегда на связи: \n"
             "+7 (999) 000-11-22 \n"
             "Но для записи лучше воспользоваться ботом — это быстро, удобно и без ожиданий!\n"
             "Мы здесь, чтобы сделать твой опыт максимально лёгким и приятным 💖",
        reply_markup=back_to_menu()
    )


def handle_feedback(update, context, param=None):
    """Оставить отзыв."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Спасибо, что решили поделиться с нами обратной связью! '
             'Напишите, пожалуйста, своё сообщение — это может быть отзыв, идея или предложение.\n\n'
             'Если хотите, чтобы менеджер с вами связался, не забудьте об этом упомянуть 🌸'
    )
    context.user_data['waiting_feedback'] = True
