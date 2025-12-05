# habits/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from habits.models import Habit
from datetime import time


HABIT_LIST_URL = reverse('habits:my_habits-list')
PUBLIC_HABIT_LIST_URL = reverse('habits:public_habits')


class HabitTestCase(APITestCase):
    """
    Класс для тестирования CRUD операций, валидаторов и прав доступа модели Habit.
    """

    def setUp(self):
        """Настройка тестовых данных и пользователей."""
        # 1. Создание пользователей
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            telegram_id='123456789'
        )
        self.another_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword',
            telegram_id='987654321'
        )

        # Авторизация основного пользователя
        self.client.force_authenticate(user=self.user)

        # 2. Создание базовых привычек
        # Полезная привычка с вознаграждением (Своя, приватная)
        self.good_habit_reward = Habit.objects.create(
            user=self.user,
            place='Парк',
            time=time(8, 0, 0),
            action='Пробежка',
            is_pleasant=False,
            reward='Чашка кофе',
            periodicity=1,
            time_to_complete=60,
            is_public=False
        )

        # Приятная привычка (Своя, приватная)
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time=time(19, 0, 0),
            action='Послушать музыку',
            is_pleasant=True,
            reward=None,
            related_habit=None,
            periodicity=1,
            time_to_complete=30,
            is_public=False
        )

        # Полезная привычка со связанной привычкой (Своя, публичная)
        self.good_habit_related = Habit.objects.create(
            user=self.user,
            place='Офис',
            time=time(14, 0, 0),
            action='Выпить стакан воды',
            is_pleasant=False,
            reward=None,
            related_habit=self.pleasant_habit,
            periodicity=2,
            time_to_complete=10,
            is_public=True
        )

        # Публичная привычка другого пользователя
        self.public_habit_other = Habit.objects.create(
            user=self.another_user,
            place='Гостиная',
            time=time(20, 0, 0),
            action='Почитать новости',
            is_pleasant=False,
            reward='Десерт',
            periodicity=7,
            time_to_complete=120,
            is_public=True
        )

    # ------------------ ТЕСТЫ ВАЛИДАТОРОВ (СОЗДАНИЕ) ------------------

    def test_habit_create_success(self):
        """Тестирование успешного создания привычки с вознаграждением. (Исправлен KeyError: 'user')"""
        data = {
            "place": "Кухня",
            "time": "09:00:00",
            "action": "Съесть яблоко",
            "is_pleasant": False,
            "reward": "Похвала",
            "related_habit": None,
            "periodicity": 3,
            "time_to_complete": 50,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Съесть яблоко')

    def test_habit_create_with_related_habit_success(self):
        """Тестирование успешного создания привычки со связанной привычкой."""
        data = {
            "place": "Рабочий стол",
            "time": "15:00:00",
            "action": "Сделать зарядку",
            "is_pleasant": False,
            "reward": None,
            "related_habit": self.pleasant_habit.id,
            "periodicity": 5,
            "time_to_complete": 100,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['related_habit'], self.pleasant_habit.id)

    def test_time_to_complete_validation_failure(self):
        """Тестирование валидатора: время выполнения > 120 секунд."""
        data = {
            "place": "Парк",
            "time": "07:00:00",
            "action": "Долгая пробежка",
            "is_pleasant": False,
            "reward": "Завтрак",
            "related_habit": None,
            "periodicity": 3,
            "time_to_complete": 150,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('time_to_complete', response.data)
        self.assertIn("не должно превышать 120 секунд", response.data['time_to_complete'][0])

    def test_reward_and_related_habit_simultaneously_validation_failure(self):
        """Тестирование валидатора: нельзя одновременно иметь reward и related_habit."""
        data = {
            "place": "Дом",
            "time": "11:00:00",
            "action": "Позвонить маме",
            "is_pleasant": False,
            "related_habit": self.pleasant_habit.id,
            "reward": "Дополнительный сон",
            "periodicity": 1,
            "time_to_complete": 30,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn("Нельзя одновременно выбрать связанную привычку и указать вознаграждение.",
                      response.data['non_field_errors'][0])

    def test_pleasant_habit_has_reward_validation_failure(self):
        """Тестирование валидатора: приятная привычка не может иметь вознаграждения."""
        data = {
            "place": "Лес",
            "time": "15:00:00",
            "action": "Погулять",
            "is_pleasant": True,
            "reward": "Новый рюкзак",
            "related_habit": None,
            "periodicity": 1,
            "time_to_complete": 100,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn("Приятная привычка не может иметь ни вознаграждения, ни связанной привычки.",
                      response.data['non_field_errors'][0])

    def test_related_habit_is_not_pleasant_validation_failure(self):
        """Тестирование валидатора: связанная привычка должна быть приятной. (Исправлен AssertionError)"""
        data = {
            "place": "Офис",
            "time": "16:00:00",
            "action": "Ответить на 5 писем",
            "is_pleasant": False,
            "reward": None,
            "related_habit": self.good_habit_reward.id,
            "periodicity": 1,
            "time_to_complete": 120,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Теперь ожидаем ошибку в non_field_errors
        self.assertIn('non_field_errors', response.data)
        self.assertIn(
            "В качестве связанной привычки можно выбрать только ту, у которой установлен признак приятной привычки.",
            response.data['non_field_errors'][0])

    def test_periodicity_more_than_seven_days_validation_failure(self):
        """Тестирование валидатора: периодичность > 7 дней (не реже, чем 1 раз в 7 дней)."""
        data = {
            "place": "Горы",
            "time": "10:00:00",
            "action": "Пеший поход",
            "is_pleasant": False,
            "reward": "Сон",
            "related_habit": None,
            "periodicity": 8,  # Ошибка
            "time_to_complete": 60,
            "is_public": False
        }
        response = self.client.post(HABIT_LIST_URL, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('periodicity', response.data)
        self.assertIn("должна быть в диапазоне от 1 до 7 дней.", response.data['periodicity'][0])

    # ------------------ ТЕСТЫ ПРАВ ДОСТУПА И СПИСКОВ ------------------

    def test_list_my_habits(self):
        """Тестирование получения списка личных привычек с пагинацией (должен включать только свои)."""
        response = self.client.get(HABIT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertFalse(
            any(habit['id'] == self.public_habit_other.id for habit in response.data['results'])
        )

    def test_list_public_habits(self):
        """Тестирование получения списка публичных привычек (должен включать публичные свои и чужие)."""
        response = self.client.get(PUBLIC_HABIT_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertTrue(
            any(habit['id'] == self.public_habit_other.id for habit in response.data['results'])
        )

    def test_unauthenticated_access_denied(self):
        """Тестирование: неавторизованный пользователь не может просматривать список."""
        self.client.force_authenticate(user=None)
        response = self.client.get(HABIT_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_other_user_habit_forbidden(self):
        """Тестирование: пользователь не может обновить чужую привычку."""
        detail_url = reverse('habits:my_habits-detail', kwargs={'pk': self.public_habit_other.pk})
        data = {'action': 'Новое действие'}

        response = self.client.patch(detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_my_habit_success(self):
        """Тестирование успешного удаления своей привычки."""
        habit_count_before = Habit.objects.count()
        detail_url = reverse('habits:my_habits-detail', kwargs={'pk': self.good_habit_reward.pk})

        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), habit_count_before - 1)
