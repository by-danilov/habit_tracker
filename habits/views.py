from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.permissions import IsOwner, IsOwnerOrReadOnly
from habits.paginators import HabitPaginator

class MyHabitViewSet(viewsets.ModelViewSet):
    """
    CRUD для личных привычек пользователя.
    """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner] # Только аутентифицированный владелец
    pagination_class = HabitPaginator # Применяем пагинацию

    def get_queryset(self):
        """
        Возвращает только привычки, созданные текущим пользователем.
        """
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Автоматически присваивает текущего пользователя как создателя.
        """
        serializer.save(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """
    Список всех публичных привычек. Только для чтения.
    """
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated] # Доступен только аутентифицированным пользователям
    pagination_class = HabitPaginator # Применяем пагинацию

    def get_queryset(self):
        """
        Возвращает только привычки, помеченные как публичные (is_public=True).
        """
        return Habit.objects.filter(is_public=True)