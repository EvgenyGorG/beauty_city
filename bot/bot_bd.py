import os
from collections import defaultdict
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_city.settings')

import django
django.setup()

from django.utils import timezone
from beauty_city_data.models import *


def get_appointments(user_id):
    appointments = Appointment.objects.filter(client__user_id=user_id)

    return appointments


def get_service_duration(service):
    return Service.objects.get(name=service).duration


def create_appointment(client_id, full_name, salon, master, service, start_datetime, end_datetime):
    client = Client.objects.get(user_id=client_id, full_name=full_name)
    salon = Salon.objects.get(name=salon)
    master = Master.objects.get(full_name=master)
    service = Service.objects.get(name=service)

    Appointment.objects.create(
        client=client, salon=salon, master=master,
        service=service, start_datetime=start_datetime, end_datetime=end_datetime
    )


def create_client(id, full_name, phone_number):
    Client.objects.create(user_id=id, full_name=full_name, phone_number=phone_number)


def get_service_price(service):
    price = Service.objects.get(name=service).price

    return price


def get_masters_address(master):
    master = Master.objects.get(full_name=master)

    return master.salon.name


def get_masters_by_category(category):
    masters = Master.objects.filter(category__name=category).values_list('full_name', flat=True)

    masters_list = [[master] for master in masters]

    return masters_list


def get_masters(salon, category):
    masters = Master.objects.filter(
        salon__name=salon, category__name=category
    ).values_list('full_name', flat=True)

    masters_list = [[master] for master in masters]

    return masters_list


def get_available_slots(master, service, days_ahead=7, interval_minutes=15):
    service = Service.objects.get(name=service)
    master = Master.objects.get(full_name=master)
    salon = master.salon
    now = timezone.localtime()
    today = now.date()
    end_date = today + timedelta(days=days_ahead)

    # Получаем все записи мастера на период
    appointments = master.appointments.filter(
        start_datetime__date__gte=today,
        start_datetime__date__lte=end_date
    ).order_by('start_datetime')

    busy_intervals = [(appt.start_datetime, appt.end_datetime) for appt in appointments]

    available_slots = defaultdict(list)  # ключ - дата, значение - список времен

    for day_offset in range(days_ahead + 1):
        current_date = today + timedelta(days=day_offset)
        open_dt = timezone.make_aware(datetime.combine(current_date, salon.open_time))
        close_dt = timezone.make_aware(datetime.combine(current_date, salon.close_time))

        # Определяем стартовую точку для слотов
        if current_date == today:
            start_time = now
            # Округляем вверх до ближайшего интервала
            minute = ((start_time.minute // interval_minutes) + 1) * interval_minutes
            hour = start_time.hour
            if minute >= 60:
                minute -= 60
                hour += 1
            start_time = start_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if start_time < open_dt:
                start_time = open_dt
        else:
            start_time = open_dt

        slot_start = start_time
        while slot_start + service.duration <= close_dt:
            slot_end = slot_start + service.duration

            # Проверяем пересечение с busy_intervals
            if not any(slot_start < busy_end and slot_end > busy_start for busy_start, busy_end in busy_intervals):
                date_str = current_date.strftime('%Y-%m-%d')
                time_str = slot_start.strftime('%H:%M')
                available_slots[date_str].append(time_str)

            slot_start += timedelta(minutes=interval_minutes)

    return dict(available_slots)

