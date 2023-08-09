## invite-system
### Простая реферальная система (тестовое задание).

Информация о профилях пользователей хранится в PostgreSQL. Невалидные JWT-токены авторизации хранятся в Redis.

1. Склонируйте репозиторий.
2. Создайте виртуальное окружение и установите зависимости из requirements.txt:

```
   pip install -r requirements.txt
```

3. Запустите докер-контейнеры с БД PostgreSQL и Redis:

```
   docker run --name invite_pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=pgpass -e POSTGRES_DB=invite_system_db -p 5432:5432 -d postgres:15
```

```
   docker run --name invite_rd -p 6379:6379 -d redis:latest
```

4. Создайте .env-file из .env.example.
5. Примените миграции: из директории "invite-system" выполните команду:

```
    python manage.py migrate
```

6. Запустите отладочный сервер Django: из директории "invite-system" выполните команду:
   
```
    python manage.py runserver 127.0.0.1:8001
```

10. Браузерная версия:

```
    http://127.0.0.1:8001/auth/authorize/
```

11. Краткое описание API-эндпоинтов:
   
```
   http://127.0.0.1:8001/api/v1/auth/authorize/
   POST, "Ввод номера телефона"
   schema: {"phone_number": string}

   http://127.0.0.1:8001/api/v1/auth/confirm-phone/{phone_number}/
   POST, "Подтверждение номера телефона"
   schema: {"auth_code": string}

   http://127.0.0.1:8001/api/v1/auth/profile/{id}/
   GET, "Получение профиля пользователя"
   Header: Authorization

   http://127.0.0.1:8001/api/v1/auth/profile/{id}/activate/
   POST, "Активация инвайт-кода"
   Header: Authorization
   schema: {"invite_code": string}

   http://127.0.0.1:8001/api/v1/auth/out/
   POST, "Выход из системы"
   Header: Authorization
```

Коллекция Postman: https://api.postman.com/collections/24474482-45bf80a9-63a7-4f54-9e02-c511975ee5df?access_key=PMAT-01H7DBJDX6QGQSHW70J32YHKP0