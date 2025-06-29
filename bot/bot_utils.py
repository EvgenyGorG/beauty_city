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

    services = menu_constants.CATEGORY_TO_SERVICES.get(service_category, [])

    query.edit_message_text(
        text=f"Вы выбрали категорию: {service_category}. Теперь выберите конкретную услугу:",
        reply_markup=build_keyboard('choose_service', services)
    )


def handle_concrete_service(update, context, param=None):
    query = update.callback_query
    query.answer()

    booking = context.user_data.get('booking', {})
    service_category = booking.get('service_category')

    if not service_category or param is None:
        query.edit_message_text("Ошибка выбора услуги. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    services_list = menu_constants.CATEGORY_TO_SERVICES.get(service_category, [])
    selected_service = services_list[index][0]

    booking['service'] = selected_service
    context.user_data['booking'] = booking

    query.edit_message_text(
        text=f"Вы выбрали услугу: {selected_service}\n\nТеперь выберите мастера:",
        reply_markup=build_keyboard('choose_master', menu_constants.CATEGORY_TO_MASTERS.get(service_category, []))
    )


def handle_choose_master(update, context, param=None):
    query = update.callback_query
    query.answer()

    booking = context.user_data.get('booking', {})
    service_category = booking.get('service_category')

    index = int(param)
    masters_list = menu_constants.CATEGORY_TO_MASTERS.get(service_category, [])
    selected_master = masters_list[index][0]

    booking['master'] = selected_master
    context.user_data['booking'] = booking

    query.edit_message_text(
        text="Выберите дату для записи:",
        reply_markup=build_keyboard('choose_date', menu_constants.AVAILABLE_DATES)
    )
    context.user_data['current_step'] = 'choose_date'


def handle_choose_date(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param is not None:
        index = int(param)
        selected_date = menu_constants.AVAILABLE_DATES[index][0]
        context.user_data['selected_date'] = selected_date

        reply_markup = build_keyboard('choose_time', menu_constants.AVAILABLE_TIMES)
        query.edit_message_text(
            text=f"Вы выбрали дату: {selected_date}\nТеперь выберите время:",
            reply_markup=reply_markup
        )
    else:
        reply_markup = build_keyboard('choose_date', menu_constants.AVAILABLE_DATES)
        query.edit_message_text(
            text="Выберите дату:",
            reply_markup=reply_markup
        )


def handle_choose_time(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param is not None:
        selected_time = menu_constants.AVAILABLE_TIMES[int(param)][0]
        context.user_data['selected_time'] = selected_time

        selected_date = context.user_data.get('selected_date', 'не выбрана')
        query.edit_message_text(
            text=f"Вы выбрали: {selected_date} в {selected_time}.\n\nТеперь напишите, пожалуйста, своё имя:"
        )

        context.user_data['current_step'] = 'ask_name'
    else:
        reply_markup = build_keyboard('choose_time', menu_constants.AVAILABLE_TIMES)
        query.edit_message_text(
            text="Выберите время:",
            reply_markup=reply_markup
        )


def handle_ask_name(update, context, param=None):
    user_data = context.user_data
    user_name = update.message.text.strip()

    user_data['name'] = user_name
    user_data['current_step'] = 'ask_phone'  # переходим к следующему шагу

    update.message.reply_text(
        f"Спасибо, {user_name}! 🌸\n\nПожалуйста, введите ваш номер телефона:"
    )


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def handle_ask_phone(update, context, param=None):
    user_data = context.user_data
    phone = update.message.text.strip()

    user_data['phone'] = phone
    # Не сбрасываем current_step, чтобы дождаться подтверждения записи

    booking = user_data.get('booking', {})
    selected_date = user_data.get('selected_date', 'не выбрана')
    selected_time = user_data.get('selected_time', 'не выбрано')
    user_name = user_data.get('name', 'не указано')

    policy_url = "https://drive.google.com/file/d/1woTyqjWjcvs8geKT56oJbdK5zKw3G3Rm/view?usp=sharing"

    confirmation_message = (
        f"Спасибо, {user_name}! 🌸\n\n"
        f"Вы планируете записаться на услугу *{booking.get('service')}* "
        f"по адресу *{booking.get('address')}*,\n"
        f"к мастеру *{booking.get('master')}*,\n"
        f"на *{selected_date} в {selected_time}*.\n"
        f"Ваш номер телефона для связи: *{phone}*.\n\n"
        f"Подтверждая свою запись, вы даете добровольное информированное согласие на хранение и обработку "
        f"персональных данных (имя, номер телефона) в соответствии с "
        f"[Политикой]({policy_url})."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Подтвердить запись", callback_data='confirm_booking'),
            InlineKeyboardButton("Отменить запись и удалить данные", callback_data='cancel_booking'),
        ]
    ])

    update.message.reply_text(
        confirmation_message,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


def handle_manage_bookings(update, context, param=None):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Здесь будет управление вашими записями"
    )


def handle_confirm_booking(update, context, param=None):
    user_data = context.user_data

    booking = user_data.get('booking', {})  # <-- обязательно словарь по умолчанию
    selected_date = user_data.get('selected_date', 'не выбрана')
    selected_time = user_data.get('selected_time', 'не выбрано')
    user_name = user_data.get('name', 'не указано')

    confirm_text = (
        f"🎉 Отлично! Ваша запись на *{booking.get('service', 'услугу')}*\n"
        f"📅 {selected_date}, ⏰ {selected_time} успешно подтверждена.\n\n"
        "Спасибо, что выбрали BeautyCity! Мы с нетерпением ждём вас 😊\n"
        "Если понадобится что-то изменить — просто напишите нам или управляйте вашей записью в главном меню бота!"
    )

    reply_markup = back_to_menu()

    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(confirm_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        update.message.reply_text(confirm_text, parse_mode='Markdown', reply_markup=reply_markup)

    user_data['current_step'] = None


def handle_cancel_booking(update, context, param=None):
    user_data = context.user_data

    user_data.pop('booking', None)
    user_data.pop('selected_date', None)
    user_data.pop('selected_time', None)
    user_data['current_step'] = None

    cancel_text = (
        "❌ Ваша запись отменена.\n"
        "Если захотите записаться снова — просто начните с главного меню."
    )

    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(cancel_text, reply_markup=back_to_menu())
    else:
        update.message.reply_text(cancel_text, reply_markup=back_to_menu())


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
