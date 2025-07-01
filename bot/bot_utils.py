from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import menu_constants
import bot_bd


def build_keyboard(action_type, button_rows):
    """Создает клавиатуру, принимает тип действия (для callback_data) и список списков с названиями кнопок."""
    keyboard = [
        [InlineKeyboardButton(text=button_label, callback_data=f"{action_type}_{row_index}")]
        for row_index, [button_label] in enumerate(button_rows)
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu():
    """Создает кнопку возврата в главное меню."""
    keyboard = [[InlineKeyboardButton(text='⬅️ Вернуться в главное меню', callback_data='to_menu')]]
    return InlineKeyboardMarkup(keyboard)


def handle_back_to_menu(update, context, param=None):
    """Обработчик кнопки возврата в главное меню."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Что вас интересует?",
        reply_markup=build_keyboard('main_menu', menu_constants.MAIN_MENU)
    )


def handle_main_menu(update, context, param=None):
    """Обработчик кнопок главного меню."""
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

    addresses = bot_bd.get_addresses_of_salons()
    categories_of_services = bot_bd.get_categories_of_services()

    if param == '0':
        context.user_data['booking'] = {'type': 'by_address'}
        query.edit_message_text(
            text="Вы выбрали запись по адресу. Выберите салон:",
            reply_markup=build_keyboard('choose_address', addresses)
        )
        context.user_data['current_step'] = 'choose_address'
    elif param == '1':
        context.user_data['booking'] = {'type': 'by_master'}
        query.edit_message_text(
            text="Вы выбрали запись к любимому мастеру. Выберите категорию услуги:",
            reply_markup=build_keyboard('choose_service_category', categories_of_services)
        )
        context.user_data['current_step'] = 'choose_service_category'
    else:
        query.edit_message_text("Неверный выбор. Попробуйте снова.", reply_markup=back_to_menu())


def handle_choose_address(update, context, param=None):
    query = update.callback_query
    query.answer()

    addresses = bot_bd.get_addresses_of_salons()
    categories_of_services = bot_bd.get_categories_of_services()

    if param is None:
        query.edit_message_text("Ошибка выбора адреса. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    address = addresses[index][0]

    if 'booking' not in context.user_data:
        context.user_data['booking'] = {}

    context.user_data['booking']['address'] = address
    context.user_data['current_step'] = 'choose_service_category'

    query.edit_message_text(
        text=f"Вы выбрали: {address}\n\nТеперь выберите категорию услуги:",
        reply_markup=build_keyboard('choose_service_category', categories_of_services)
    )


def handle_choose_service_category(update, context, param=None):
    query = update.callback_query
    query.answer()

    categories_of_services = bot_bd.get_categories_of_services()

    if param is None:
        query.edit_message_text("Ошибка выбора категории услуги. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    service_category = categories_of_services[index][0]

    if 'booking' not in context.user_data:
        context.user_data['booking'] = {}

    context.user_data['booking']['service_category'] = service_category

    booking_type = context.user_data['booking'].get('type')
    context.user_data['current_step'] = 'choose_master'

    if booking_type == 'by_master':
        masters_list = bot_bd.get_masters_by_category(service_category)
        query.edit_message_text(
            text="Вы выбрали категорию: {}.\nТеперь выберите мастера:".format(service_category),
            reply_markup=build_keyboard('choose_master', masters_list)
        )
        context.user_data['current_step'] = 'choose_master'
    else:
        services = bot_bd.get_services(service_category)
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
    services_list = bot_bd.get_services(service_category)
    selected_service = services_list[index][0]

    booking['service'] = selected_service
    context.user_data['booking'] = booking

    if booking.get('type') == 'by_address':
        salon = booking.get('address')
        masters_list = bot_bd.get_masters(salon, service_category)
        query.edit_message_text(
            text="Вы выбрали услугу: {}.\n\nТеперь выберите мастера:".format(selected_service),
            reply_markup=build_keyboard('choose_master', masters_list)
        )
        context.user_data['current_step'] = 'choose_master'

    else:
        available_dates = bot_bd.get_available_slots(booking['master'], booking['service']).keys()
        available_dates = [[date] for date in available_dates]
        query.edit_message_text(
            text=f"Вы выбрали услугу: {selected_service}\n\nТеперь выберите дату:",
            reply_markup=build_keyboard('choose_date', available_dates)
        )
        context.user_data['current_step'] = 'choose_date'


def handle_choose_master(update, context, param=None):
    query = update.callback_query
    query.answer()

    booking = context.user_data.get('booking', {})
    service_category = booking.get('service_category')
    booking_type = booking.get('type')

    if booking_type == 'by_address':
        salon = booking.get('address')
        masters_list = bot_bd.get_masters(salon, service_category)
        index = int(param)
        selected_master = masters_list[index][0]
        booking['master'] = selected_master
        context.user_data['booking'] = booking
        available_dates = bot_bd.get_available_slots(booking['master'], booking['service']).keys()
        available_dates = [[date] for date in available_dates]

        query.edit_message_text(
            text=f"Вы выбрали мастера: {selected_master}.\nТеперь выберите дату:",
            reply_markup=build_keyboard('choose_date', available_dates)
        )
        context.user_data['current_step'] = 'choose_date'
    else:
        masters_list = bot_bd.get_masters_by_category(service_category)
        index = int(param)
        selected_master = masters_list[index][0]
        booking['master'] = selected_master
        booking['address'] = bot_bd.get_masters_address(booking['master'])
        context.user_data['booking'] = booking
        services = bot_bd.get_services(service_category)
        query.edit_message_text(
            text="Выберите услугу:",
            reply_markup=build_keyboard('choose_service', services)
        )
        context.user_data['current_step'] = 'choose_service_after_master'


def handle_choose_service_after_master(update, context, param=None):
    query = update.callback_query
    query.answer()

    if param is None:
        query.edit_message_text("Ошибка выбора услуги. Попробуйте снова.", reply_markup=back_to_menu())
        return

    index = int(param)
    category = context.user_data.get('booking', {}).get('service_category')
    service = bot_bd.get_services(category)[index][0]

    booking = context.user_data.get('booking', {})
    booking['service'] = service
    context.user_data['booking'] = booking

    available_dates = bot_bd.get_available_slots(booking['master'], booking['service']).keys()
    available_dates = [[date] for date in available_dates]

    query.edit_message_text(
        text="Выберите дату для записи:",
        reply_markup=build_keyboard('choose_date', available_dates)
    )
    context.user_data['current_step'] = 'choose_date'


def handle_choose_date(update, context, param=None):
    query = update.callback_query
    query.answer()

    booking = context.user_data.get('booking', {})
    available_slots = bot_bd.get_available_slots(booking['master'], booking['service'])
    available_dates = [[date] for date in available_slots.keys()]

    if param is not None:
        index = int(param)
        selected_date = available_dates[index][0]
        context.user_data['selected_date'] = selected_date
        available_times = available_slots[selected_date]
        available_times = [[time] for time in available_times]

        reply_markup = build_keyboard('choose_time', available_times)
        query.edit_message_text(
            text=f"Вы выбрали дату: {selected_date}\nТеперь выберите время:",
            reply_markup=reply_markup
        )
    else:
        reply_markup = build_keyboard('choose_date', available_dates)
        query.edit_message_text(
            text="Выберите дату:",
            reply_markup=reply_markup
        )
    context.user_data['current_step'] = 'choose_date'


def handle_choose_time(update, context, param=None):
    query = update.callback_query
    query.answer()

    booking = context.user_data.get('booking', {})
    available_times = bot_bd.get_available_slots(
        booking['master'], booking['service']
    )[context.user_data['selected_date']]
    available_times = [[time] for time in available_times]

    if param is not None:
        selected_time = available_times[int(param)][0]
        context.user_data['selected_time'] = selected_time

        selected_date = context.user_data.get('selected_date', 'не выбрана')
        query.edit_message_text(
            text=f"Вы выбрали: {selected_date} в {selected_time}.\n\nТеперь напишите, пожалуйста, своё имя:"
        )

        context.user_data['current_step'] = 'ask_name'
    else:
        reply_markup = build_keyboard('choose_time', available_times)
        query.edit_message_text(
            text="Выберите время:",
            reply_markup=reply_markup
        )
        context.user_data['current_step'] = 'ask_name'


def handle_ask_name(update, context, param=None):
    user_data = context.user_data
    user_name = update.message.text.strip()

    user_data['name'] = user_name
    user_data['current_step'] = 'ask_phone'

    update.message.reply_text(
        f"Спасибо, {user_name}! 🌸\n\nПожалуйста, введите ваш номер телефона:"
    )


def handle_ask_phone(update, context, param=None):
    user_data = context.user_data
    phone = update.message.text.strip()

    user_data['phone'] = phone

    booking = user_data.get('booking', {})
    booking['price'] = bot_bd.get_service_price(booking['service'])
    selected_date = user_data.get('selected_date', 'не выбрана')
    selected_time = user_data.get('selected_time', 'не выбрано')
    user_name = user_data.get('name', 'не указано')

    policy_url = "https://drive.google.com/file/d/1woTyqjWjcvs8geKT56oJbdK5zKw3G3Rm/view?usp=sharing"

    confirmation_message = (
        f"Спасибо, {user_name}! 🌸\n\n"
        f"Вы планируете записаться на услугу *{booking.get('service')}* "
        f"Стоимость {booking['price']},\n"
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

    user_id = update.effective_user.id
    appointments = bot_bd.get_appointments(user_id)

    if appointments.exists():
        text_lines = ["Ваши записи:\n"]

        for i, appointment in enumerate(appointments, start=1):
            start_dt = appointment.start_datetime.strftime("%d.%m.%Y %H:%M")
            end_dt = appointment.end_datetime.strftime("%H:%M")

            text_lines.append(
                f"{i}. Мастер: {appointment.master.full_name}\n"
                f"   Услуга: {appointment.service.name}\n"
                f"   Дата и время: {start_dt} - {end_dt}\n"
                f"   Имя клиента: {appointment.client.full_name}\n"
            )

        query.edit_message_text(text="\n".join(text_lines), reply_markup=back_to_menu())

    else:
        query.edit_message_text(text="У вас пока нет записей.", reply_markup=back_to_menu())


def handle_confirm_booking(update, context, param=None):
    user_data = context.user_data

    booking = user_data.get('booking', {})
    selected_date = user_data.get('selected_date', 'не выбрана')
    selected_time = user_data.get('selected_time', 'не выбрано')

    confirm_text = (
        f"🎉 Отлично! Ваша запись на *{booking.get('service', 'услугу')}*\n"
        f"📅 {selected_date}, ⏰ {selected_time} успешно подтверждена.\n\n"
        "Спасибо, что выбрали BeautyCity! Мы с нетерпением ждём вас 😊\n"
        "Если понадобится что-то изменить — просто напишите нам или управляйте вашей записью в главном меню бота!"
    )

    user_id = update.effective_user.id
    bot_bd.create_client(user_id, context.user_data['name'], context.user_data['phone'])
    start_datetime = datetime.strptime(
        context.user_data['selected_date'] + " " + context.user_data['selected_time'], '%Y-%m-%d %H:%M'
    )
    service_duration = bot_bd.get_service_duration(booking['service'])
    end_datetime = start_datetime + service_duration
    bot_bd.create_appointment(
        user_id, context.user_data['name'], booking['address'], booking['master'],
        booking['service'], start_datetime, end_datetime
    )

    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(confirm_text, parse_mode='Markdown', reply_markup=back_to_menu())
    else:
        update.message.reply_text(confirm_text, parse_mode='Markdown', reply_markup=back_to_menu())

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
