# Money_control_fastapi_backend

![GitHub](https://img.shields.io/github/license/vital-yano/money_control_django_backend) ![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/vital-yano/money_control_django_backend)

### Описание
Репозиторий содержить бэкенд с использованием фреймворка Django для приложения по контролю своих расходов. Управление осуществляется с помощью телеграмм бота.
Используемый стек:
- Python 3.11
- Django
- Pytest
- Pyright
- Ruff
- Redis
- Postgres
- Docker

Postgres и Redis поднимаются в Docker.


### Инструкция по запуску проекта и работе с ним

Установка виртуального окружения и зависимостей:
```bash
python -m venv venv && source venv/bin/activate && pip install -r req.txt
```

Проверка с помощью Ruff и Pyright

```bash
ruff check
pyright
```

Запуск локальных и тестовых бд и redis:
```bash
make db_and_redis_local
```

Создание таблиц в бд:
```bash
python manage.py migrate
python manage.py migrate --settings=config.settings_test
```

Создание индексов в Redis:
```bash
python manage.py create_redis_indices
```

Запуск тестов: 
```bash
pytest src/tests
```

Запуск приложения:
```bash
python manage.py runserver
```

Документация по хэндлерам расположена по адресу:
```
127.0.0.1:8000/swagger
```

Для получения кода для регистрации используется сервис SMS.RU (с помощью звонка).
После регистрации добавьте свой SMS_API_ID в файл .env.

### Планы на будущее
На данный момент реализована только регистрация пользователей. Планируется реализовать позже:

- Статьи доходов/расходов
- Кошелёк
- Переводы
- Долги
- Бюджет
