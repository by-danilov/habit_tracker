from rest_framework import serializers
from habits.models import Habit
from habits.validators import (
    validate_time_to_complete,
    validate_periodicity,
    validate_related_habit_is_pleasant
)


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit, включающий все сложные валидаторы.
    """
    time_to_complete = serializers.IntegerField(validators=[validate_time_to_complete])
    periodicity = serializers.IntegerField(validators=[validate_periodicity])

    class Meta:
        model = Habit
        fields = '__all__'


    def validate(self, data):
        """
        Реализация сложной межполевой валидации:
        1. Исключить одновременный выбор связанной привычки и указания вознаграждения.
        2. У приятной привычки (is_pleasant=True) не может быть вознаграждения или связанной привычки.
        3. Проверка is_pleasant у связанной привычки.
        """

        # Если это обновление, данные для проверки могут быть в instance
        instance = getattr(self, 'instance', None)

        # Используем .get() для данных из запроса, чтобы не получить KeyError
        reward = data.get('reward', instance.reward if instance else None)
        related_habit = data.get('related_habit', instance.related_habit if instance else None)
        is_pleasant = data.get('is_pleasant', instance.is_pleasant if instance else False)

        # --- Валидация 1: Вознаграждение ИЛИ Связанная привычка (но не оба сразу) ---

        if related_habit and reward:
            raise serializers.ValidationError(
                "Нельзя одновременно выбрать связанную привычку и указать вознаграждение. Выберите что-то одно."
            )

        # Если привычка НЕ приятная (полезная), она должна иметь либо вознаграждение, либо связанную привычку.
        if not is_pleasant and not (related_habit or reward):
            raise serializers.ValidationError(
                "Полезная привычка (которая не является приятной) должна иметь либо вознаграждение, либо связанную привычку."
            )

        # --- Валидация 2: Приятная привычка не может иметь ни вознаграждения, ни связанной привычки ---

        if is_pleasant:
            if reward or related_habit:
                raise serializers.ValidationError(
                    "Приятная привычка не может иметь ни вознаграждения, ни связанной привычки."
                )

        # --- Валидация 3: Связанная привычка должна быть приятной ---

        validate_related_habit_is_pleasant(related_habit)

        return data
