from datetime import time

from django.db import models


class Salon(models.Model):
    name = models.CharField("название салона", max_length=200)
    open_time = models.TimeField("время открытия", default=time(10, 0))
    close_time = models.TimeField("время закрытия", default=time(20, 0))

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("название категории услуг", max_length=100)

    def __str__(self):
        return self.name


class Master(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='masters',
        verbose_name="категория услуг"
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.SET_NULL,
        null=True, related_name='masters',
        verbose_name="салон"
    )
    full_name = models.CharField("имя мастера", max_length=100)

    def __str__(self):
        return self.full_name


class Service(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='services', verbose_name="категория услуг"
    )
    name = models.CharField("наименование услуги", max_length=100)
    price = models.DecimalField(verbose_name="цена", max_digits=10, decimal_places=2)
    duration = models.DurationField(verbose_name="длительность")

    def __str__(self):
        return self.name


class Client(models.Model):
    user_id = models.IntegerField(verbose_name="телеграм id")
    full_name = models.CharField("ФИО", max_length=100)
    phone_number = models.CharField("номер телефона", max_length=100)

    def __str__(self):
        return f'{self.full_name} (ID:{self.user_id})'


class Appointment(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="клиент"
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="салон"
    )
    master = models.ForeignKey(
        Master, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="мастер"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="услуга"
    )
    start_datetime = models.DateTimeField(verbose_name="время начала")
    end_datetime = models.DateTimeField(verbose_name="время окончания")
