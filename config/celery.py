import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Инициализируем Celery
# 'config' - имя текущего модуля настроек
app = Celery('config')

# Используем настройки Django для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживать задачи во всех INSTALLED_APPS,
# ищущих файлы 'tasks.py'
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Тестовая задача для проверки работоспособности Celery."""
    print(f'Запрос: {self.request!r}')
