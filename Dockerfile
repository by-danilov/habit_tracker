# СТАДИЯ 1: СБОРКА И УСТАНОВКА ЗАВИСИМОСТЕЙ
# Используем Python 3.13
FROM python:3.13-slim AS builder

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем зависимости, необходимые для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы Poetry для установки зависимостей
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости с помощью Poetry
# --no-root: не устанавливать сам проект (пока), только зависимости
# --only main: устанавливать только основные зависимости (исключая dev)
# --no-interaction: не требовать ввода
RUN pip install poetry
RUN poetry install --no-dev --no-root --no-interaction

# СТАДИЯ 2: ФИНАЛЬНЫЙ ОБРАЗ

FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости, необходимые для выполнения
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные зависимости из стадии "builder"
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/include /usr/local/include
# Копируем Poetry-среду
COPY --from=builder /root/.cache/pypoetry /root/.cache/pypoetry

# Копируем файлы проекта
COPY . /app

# Устанавливаем Poetry в финальный образ для доступа к команде 'poetry run'
RUN pip install poetry

# Отключаем создание виртуального окружения Poetry
RUN poetry config virtualenvs.create false

# Делаем файлы исполняемыми
RUN chmod +x manage.py

# Указываем порт, который будет открывать приложение
EXPOSE 8000

# Команда, которая будет выполняться по умолчанию (переопределяется в docker-compose)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
