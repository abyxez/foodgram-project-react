Автор проекта - Константин Питонов. 

Технологии

Python 3.10
Django 4.2.4
Django REST framework 3.14
Nginx
Docker
Postgres
Gunicorn
React.JS

Документация api доступна по адресу:

http://qwertyk200.ddns.net/api/docs

Проект Foodgram - это облачный сервис для кулинаров, где вы можете подписываться на других авторов, загружать свои рецепты, а также выводить списки ингредиентов на покупку в формате .txt. Сервис поддерживает /api/, например, с помощью Postman.

Локальный запуск проекта:

git@github.com:abyxez/foodgram-project-react.git

cd foodgram-project-react

Создать и активировать виртуальное окружение:

python3 -m venv venv

Linux/macOS: source venv/bin/activate
Windows: source venv/Scripts/activate

python3 -m pip install --upgrade pip

Установить зависимости из файла requirements:

pip install -r requirements.txt

Выполнить миграции:

python3 manage.py migrate

Запустить проект:

python3 manage.py runserver

Создать суперпользователя:

python3 manage.py createsuperuser ( все поля обязательны, поэтому вместо почты можно подставить шаблон <some_letters>@a.ru )

Запуск и деплой приложения на сервере:

Установить на сервере docker и docker compose. Скопировать на сервер файлы docker-compose.yaml и default.conf:

scp docker compose.yml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yml
scp nginx.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf

sudo docker compose exec foodgram-backend-1 python manage.py migrate

sudo docker compose exec foodgram-backend-1 python manage.py collectstatic --no-input 

Создать пользователя:

sudo docker compose exec foodgram-backend-1 python manage.py createsuperuser

sudo docker compose exec backend python3 manage.py import

------------------------------------------------------

API сервис, и его эндпоинты ( можно воспользоваться Postman ):

/api/users/ Get-запрос на получение списка пользователей. POST-запрос – регистрация нового пользователя.

/api/users/{id} GET-запрос – персональная страница пользователя с указанным id.

/api/users/me/ GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям.

/api/tags/ GET-запрос — получение списка всех тегов.

/api/tags/{id} GET-запрос — получение информации о теге о его id.

/api/ingredients/ GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента.

/api/ingredients/{id}/ GET-запрос — получение информации об ингредиенте по его id.

/api/recipes/ GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

/api/recipes/?is_favorited=1 GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей.

/api/recipes/is_in_shopping_cart=1 GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей.

/api/recipes/{id}/ GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

/api/recipes/{id}/favorite/ POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей.

/api/recipes/{id}/shopping_cart/ POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей.

/api/recipes/download_shopping_cart/ GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей.

/api/users/{id}/subscribe/ GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

/api/users/subscriptions/ GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.