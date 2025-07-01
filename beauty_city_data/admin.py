from django.contrib import admin

from beauty_city_data.models import (
    Salon, Category, Master, Service,
    Client, Appointment
)


admin.site.register(Salon)
admin.site.register(Category)
admin.site.register(Master)
admin.site.register(Service)
admin.site.register(Client)
admin.site.register(Appointment)
