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

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # 2. Применяем простые, однополевые валидаторы
    time_to_complete = serializers.IntegerField(validators=[validate_time_to_complete])
    periodicity = serializers.IntegerField(validators=[validate_periodicity])

    # 3. Делаем поля reward и related_habit необязательными на уровне сериализатора
    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.all(),
        required=False,
        allow_null=True
    )
    reward = serializers.CharField(
        max_length=255,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, data):
        """
        Реализация сложной межполевой валидации.
        """

        # Получаем данные из запроса. 
        instance = getattr(self, 'instance', None)

        # Получаем значения, используя .get()
        reward = data.get('reward', instance.reward if instance else None)
        related_habit = data.get('related_habit', instance.related_habit if instance else None)
        is_pleasant = data.get('is_pleasant', instance.is_pleasant if instance else False)

        # --- 1. Вознаграждение ИЛИ Связанная привычка (но не оба сразу) ---

        if related_habit and reward:
            # Явно возвращаем non_field_errors для корректной обработки в тестах
            raise serializers.ValidationError(
                {"non_field_errors": [
                    "Нельзя одновременно выбрать связанную привычку и указать вознаграждение. Выберите что-то одно."]}
            )

        # --- 2. Полезная привычка должна иметь вознаграждение ИЛИ связанную привычку ---
        if not is_pleasant and not (related_habit or reward):
            # Явно возвращаем non_field_errors
            raise serializers.ValidationError(
                {"non_field_errors": [
                    "Полезная привычка (которая не является приятной) должна иметь либо вознаграждение, либо связанную привычку."]}
            )

        # --- 3. Приятная привычка не может иметь ни вознаграждения, ни связанной привычки ---

        if is_pleasant:
            if reward or related_habit:
                # Явно возвращаем non_field_errors
                raise serializers.ValidationError(
                    {"non_field_errors": ["Приятная привычка не может иметь ни вознаграждения, ни связанной привычки."]}
                )

        # --- 4. Связанная привычка должна быть приятной ---

        # Если related_habit есть, вызываем проверку.
        validate_related_habit_is_pleasant(related_habit)

        return data
