������ ����� gunicorn:
gunicorn -b localhost:9999 main

������ ����� uwsgi:
uwsgi --http :9999 --wsgi-file main.py