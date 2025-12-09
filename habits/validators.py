from rest_framework.exceptions import ValidationError
from habits.models import Habit, MIN_PERIODICITY_DAYS, MAX_PERIODICITY_DAYS


def validate_time_to_complete(value):
    """
    Валидатор: Время выполнения должно быть не больше 120 секунд.
    """
    MAX_SECONDS = 120
    if value > MAX_SECONDS:
        raise ValidationError(f"Время выполнения не должно превышать {MAX_SECONDS} секунд.")


def validate_periodicity(value):
    """
    Валидатор: Периодичность не реже, чем 1 раз в 7 дней.
    """
    if not (MIN_PERIODICITY_DAYS <= value <= MAX_PERIODICITY_DAYS):
        raise ValidationError(
            f"Периодичность должна быть в диапазоне от {MIN_PERIODICITY_DAYS} до {MAX_PERIODICITY_DAYS} дней."
        )


def validate_related_habit_is_pleasant(related_habit):
    """
    Валидатор: В связанные привычки могут попадать только привычки
    с признаком приятной привычки (is_pleasant=True).
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            "В качестве связанной привычки можно выбрать только ту, у которой установлен признак приятной привычки."
        )
