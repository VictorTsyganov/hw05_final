# Проект YaTube

[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)

## Описание

YaTube - социальная сеть для дневников. После регистрации на сайте, любой пользователь может вести свои записи, читать записи других пользователей и оставлять комментарии.

Разработан по классической MVT архитектуре. Используется кэширование и пагинация. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Модерация записей, работа с пользователями, создание групп осуществляется через панель администратора. Написаны тесты проверяющие работу сервиса.

## Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:VictorTsyganov/hw05_final.git ```

Создать и активировать виртуальное окружение:

``` python -m venv venv ``` 

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```
    
``` python -m pip install --upgrade pip ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

Перейти в папку yatube в командной строке:

``` cd yatube ``` 

Выполнить миграции:

``` python manage.py migrate ``` 

Запустить проект:

``` python manage.py runserver ```

Проверить работу проекта возможно по любой из ссылок:

```
http://localhost:8000/
http://127.0.0.1:8000/
```

Проект запущен на сервере по адресу: https://viktortsyganov.pythonanywhere.com/

## Системные требования
- Python 3.9+
- Works on Linux, Windows, macOS

## Стек технологий

- Python 3.9

- Django 2.2

- SQLite3

## Автор

[Виктор Цыганов](https://github.com/VictorTsyganov)
