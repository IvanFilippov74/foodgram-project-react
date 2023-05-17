## FoodGram - Продуктовый помощник
[![yamdb_final](https://github.com/IvanFilippov74/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/IvanFilippov74/yamdb_final/actions/workflows/yamdb_workflow.yml)

### Описание:
На сервисе FoodGram пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### Технологии :
![Python](https://img.shields.io/badge/Python-3.7-blue)  ![Django](https://img.shields.io/badge/Django-3.2.13-blue)  ![DjangoREST](https://img.shields.io/badge/Django%20Rest%20Framework-3.12.4-blue)  ![Docker](https://img.shields.io/badge/Docker-23.0.6-blue)  ![Nginx](https://img.shields.io/badge/Nginx-1.19.3-blue)  ![Gunicorn](https://img.shields.io/badge/Gunicorn-20.0.4-blue)  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.0-blue)
### Как запустить проект:

1. Склонировать репозиторий в командной строке:
```
https://github.com/IvanFilippov74/foodgram-project-react.git
```
Затем перейдите в корневую директорию проекта:
```
cd foodgram-project-react/
```
2. В директории infra/ создайте файл .env, и заполните его:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<ваш_пароль>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный_ключ_проекта>
```
3. Если Docker не установлен, установите его используя официальную инструкцию:
```
https://docs.docker.com/engine/install/
```
4. Перейдите в директорию ```infra```:
```
cd infra/
```
Затем запустите docker-compose, используя команду*:
```
docker-compose up -d
```
5. Создайте миграции командой:
```
docker-compose exec web python manage.py migrate
```
6. Подгрузите статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```
7. Создайте супер пользователя:
```
docker-compose exec web python manage.py createsuperuser
```
9. Проект доступен по адресу ```http://localhost/```, для админ-панели используйте ```http://localhost/admin/```, документацию по api можно посмотреть здесь > ```http://localhost/redoc/```.
10. Остановить запущенные контейнеры можно командой ```docker-compose stop```, вновь запустить ```docker-compose start```, для остановки и удаления контейнеров используйте команду ```docker-compose down -v```.

*Важное примечание для ОС Linux используйте команду ```sudo```. 
### Авторы:
Филиппов Иван

<a href="https://github.com/IvanFilippov74"><img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white"></a>