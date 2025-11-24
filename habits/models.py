from django.conf import settings
from django.db import models

# Константы для ограничения периодичности
# Нельзя выполнять привычку реже, чем 1 раз в 7 дней.
MAX_PERIODICITY_DAYS = 7
MIN_PERIODICITY_DAYS = 1


class Habit(models.Model):
    """
    Модель для отслеживания привычек.
    Основана на принципах "Атомных привычек".
    """

    # 1. Основные поля
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Создатель привычки',
    )

    place = models.CharField(
        max_length=255,
        verbose_name='Место',
        help_text='Место, в котором необходимо выполнять привычку.',
    )

    time = models.TimeField(
        verbose_name='Время',
        help_text='Время, когда необходимо выполнять привычку (например, 14:30:00).',
    )

    action = models.CharField(
        max_length=255,
        verbose_name='Действие',
        help_text='Действие, которое представляет собой привычка.',
    )

    # 2. Поля для связи и вознаграждения
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки',
        help_text='Если True, это приятная привычка, которая может быть вознаграждением для полезной.',
    )

    # Связанная привычка (может быть только приятной привычкой!)
    related_habit = models.ForeignKey(
        'self',  # Ссылка на саму себя
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Приятная привычка, которая выполняется сразу после полезной.',
    )

    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Вознаграждение',
        help_text='Текстовое вознаграждение, если нет связанной приятной привычки.',
    )

    # 3. Ограничения

    # Периодичность (1-7 дней, по умолчанию ежедневная)
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Периодичность (в днях)',
        help_text=f'Интервал повторения привычки (от {MIN_PERIODICITY_DAYS} до {MAX_PERIODICITY_DAYS} дней).',
    )

    # Время на выполнение (<= 120 секунд)
    time_to_complete = models.PositiveSmallIntegerField(
        verbose_name='Время на выполнение (в секундах)',
        help_text='Время, которое предположительно потратит пользователь (не более 120 секунд).',
    )

    # 4. Дополнительные поля
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности',
        help_text='Если True, привычка отображается в общем списке.',
    )

    class Meta:
        verbose_name = 'привычка'
        verbose_name_plural = 'привычки'
        # Сортировка по времени и по ID
        ordering = ('time', 'id',)

    def __str__(self):
        return f'Привычка: {self.action} ({self.user.username})'

