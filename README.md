# Foodgram

Адрес сервера: http://84.252.143.101/


### Описание
Проект **Foodgram** - «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.


### Запуск приложения:
* Собрать контейнеры и запустить их
  ```
  docker-compose up -d --build
  ```
* Сделать миграции
  ```
  docker-compose exec backend python manage.py makemigrations --noinput
  docker-compose exec backend python manage.py migrate --noinput
  ```
* Создать суперпользователя
  ```
  docker-compose exec backend python manage.py createsuperuser
  ```
* Подгрузить статику
  ```
  docker-compose exec backend python manage.py collectstatic --no-input
