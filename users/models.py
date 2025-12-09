from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя, наследующая от AbstractUser.
    Используется для настройки системы аутентификации Django.
    """
    telegram_id = models.CharField(
        max_length=50,
        verbose_name='ID Телеграм',
        blank=True,
        null=True,
        unique=True,
        help_text='Уникальный ID пользователя в Телеграм для рассылки уведомлений.'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.email if self.email else self.username
