# api_final

REST API для социальной сети Yatube с возможностью публикации постов, комментариев и подписок.

## Как запустить проект

1. Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/your_username/yatube_api.git
cd yatube_api
```

2. Создать и активировать виртуальное окружение:

```bash
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для macOS/Linux:
source venv/bin/activate
```
3. Установить зависимости из файла requirements.txt:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
4. Выполнить миграции:
```bash
python manage.py migrate
```
5. Создать суперпользователя (опционально):

```bash
python manage.py createsuperuser
```
6. Запустить проект:
```bash
python manage.py runserver
```

## Примеры API запросов
1. Получение списка постов
```bash
GET http://127.0.0.1:8000/api/v1/posts/
```
Пример ответа:

```json
[
    {
        "id": 1,
        "author": "username",
        "text": "Текст поста",
        "pub_date": "2023-01-01T12:00:00Z",
        "image": null,
        "group": null
    }
]
```
2. Создание нового поста (требуется аутентификация)
```bash
POST http://127.0.0.1:8000/api/v1/posts/
Headers:
Authorization: Bearer <ваш_token>
Content-Type: application/json
Body:
{
    "text": "Новый пост",
    "image": "<base64_encoded_image>",
    "group": 1
}
```
3. Получение комментариев к посту
```bash
GET http://127.0.0.1:8000/api/v1/posts/1/comments/
Подписка на пользователя (требуется аутентификация)
bash
POST http://127.0.0.1:8000/api/v1/follow/
Headers:
Authorization: Bearer <ваш_token>
Content-Type: application/json

Body:
{
    "following": "username_to_follow"
}
```
## Документация API
После запуска проекта полная документация API доступна по адресу:
```link
http://127.0.0.1:8000/redoc/ (ReDoc)
```

## Технологии
Python 3.9+

Django 3.2

Django REST Framework 3.12

Simple JWT для аутентификации

SQLite (для разработки)