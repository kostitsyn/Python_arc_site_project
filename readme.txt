Запуск через gunicorn:
gunicorn -b localhost:9999 main

Запуск через uwsgi:
uwsgi --http :9999 --wsgi-file main.py