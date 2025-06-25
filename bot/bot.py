import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beauty_city.settings")
django.setup()

# from app.models import YourModel  # импорт моделей после настройки Django

# Далее код бота...