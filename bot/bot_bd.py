import os
from collections import defaultdict
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_city.settings')

import django
django.setup()

from django.utils import timezone
from beauty_city_data.models import (
    Salon, Master, Client, Service, Appointment, Category
)


def get_categories_of_services():
    categories = Category.objects.all().values_list('name')

    return [list(category) for category in categories]


def get_addresses_of_salons():
    salons = Salon.objects.all().values_list('name')

    return [list(salon) for salon in salons]


def get_masters_by_category(category):
    masters = Master.objects.filter(category__name=category).values_list('full_name')

    return [list(master) for master in masters]


def get_services(category):
    services = Service.objects.filter(category__name=category).values_list('name')

    return [list(service) for service in services]


def get_masters(salon_name, category):
    masters = Master.objects.filter(
        salon__name=salon_name, category__name=category
    ).values_list('full_name')

    return [list(master) for master in masters]


def get_appointments(user_id):
    return Appointment.objects.filter(client__user_id=user_id)


def get_service_duration(service):
    return Service.objects.get(name=service).duration


def create_appointment(
        client_id, full_name, salon_name,
        master_name, service, start_datetime,
        end_datetime
):
    client = Client.objects.get(user_id=client_id, full_name=full_name)
    salon = Salon.objects.get(name=salon_name)
    master = Master.objects.get(full_name=master_name)
    service = Service.objects.get(name=service)

    Appointment.objects.create(
        client=client, salon=salon, master=master,
        service=service, start_datetime=start_datetime, end_datetime=end_datetime
    )


def create_client(user_id, full_name, phone_number):
    Client.objects.create(user_id=user_id, full_name=full_name, phone_number=phone_number)


def get_service_price(service):
    return Service.objects.get(name=service).price


def get_masters_address(master_name):
    master = Master.objects.get(full_name=master_name)

    return master.salon.name


def get_available_slots(master_name, service, days_ahead=7, interval_minutes=15):
    service = Service.objects.get(name=service)
    master = Master.objects.get(full_name=master_name)
    salon = master.salon

    now = timezone.localtime()
    today = now.date()
    end_date = today + timedelta(days=days_ahead)

    appointments = master.appointments.filter(
        start_datetime__date__gte=today,
        start_datetime__date__lte=end_date
    ).order_by('start_datetime')

    busy_intervals = [
        (appointment.start_datetime, appointment.end_datetime) for appointment in appointments
    ]

    available_slots = defaultdict(list)

    for day_offset in range(days_ahead + 1):
        current_date = today + timedelta(days=day_offset)
        open_dt = timezone.make_aware(datetime.combine(current_date, salon.open_time))
        close_dt = timezone.make_aware(datetime.combine(current_date, salon.close_time))

        if current_date == today:
            start_time = now
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

            if not any(slot_start < busy_end and slot_end > busy_start for busy_start, busy_end in busy_intervals):
                date_str = current_date.strftime('%Y-%m-%d')
                time_str = slot_start.strftime('%H:%M')
                available_slots[date_str].append(time_str)

            slot_start += timedelta(minutes=interval_minutes)

    return dict(available_slots)

