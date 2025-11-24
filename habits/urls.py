from django.urls import path
from rest_framework.routers import DefaultRouter

from habits.views import MyHabitViewSet, PublicHabitListView

# Создаем роутер для автоматической генерации URL для CRUD
router = DefaultRouter()
router.register(r'my', MyHabitViewSet, basename='my_habits')

urlpatterns = [
    # CRUD для личных привычек
    *router.urls,

    # Список публичных привычек
    path('public/', PublicHabitListView.as_view(), name='public_habits'),
]
