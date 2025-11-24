import datetime
from celery import shared_task
from django.conf import settings
from habits.models import Habit
import telegram

# Инициализируем бота
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


@shared_task
def send_habit_reminders():
    """
    Отложенная задача Celery для отправки напоминаний о привычках.
    Задача должна запускаться периодически (например, раз в час или минуту).
    """
    # Определяем текущее время
    now = datetime.datetime.now()
    current_time = now.time().replace(minute=0, second=0, microsecond=0)

    # Ищем привычки, которые должны быть выполнены в текущем часовом окне
    habits_to_remind = Habit.objects.filter(
        time__hour=now.hour,
        user__telegram_id__isnull=False  # Напоминаем только тем, у кого есть ID
    )

    if not habits_to_remind.exists():
        print(f"[{now.strftime('%H:%M')}] Напоминаний не найдено.")
        return

    for habit in habits_to_remind:
        # Формируем сообщение
        message = (
            f"🔔 *Напоминание о привычке!* 🔔\n\n"
            f"**Действие:** Я буду {habit.action}\n"
            f"**Когда:** в {habit.time.strftime('%H:%M')}\n"
            f"**Где:** в {habit.place}\n\n"
        )

        if habit.reward:
            message += f"**Вознаграждение:** {habit.reward}\n"
        elif habit.related_habit:
            message += f"**Связанная привычка:** {habit.related_habit.action}\n"

        try:
            # Отправляем сообщение в Telegram
            bot.send_message(
                chat_id=habit.user.telegram_id,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            print(f"Отправлено напоминание пользователю {habit.user.username} о привычке '{habit.action}'.")

        except telegram.error.TelegramError as e:
            print(f"Ошибка отправки сообщения пользователю {habit.user.username}: {e}")

    print(f"[{now.strftime('%H:%M')}] Рассылка завершена. Отправлено {habits_to_remind.count()} напоминаний.")
