from rest_framework import serializers
from users.models import User # Импортируем нашу новую модель

class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя (регистрация)."""
    class Meta:
        model = User
        # Включаем все поля, необходимые для регистрации, включая username и password
        fields = ('id', 'email', 'username', 'password', 'telegram_id')
        extra_kwargs = {'password': {'write_only': True}} # Пароль только для записи

    def create(self, validated_data):
        # Переопределяем метод create для безопасного хеширования пароля
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            telegram_id=validated_data.get('telegram_id'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя (после регистрации/авторизации)."""
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'telegram_id', 'is_staff')
