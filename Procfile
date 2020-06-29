release: python manage.py migrate
release: rm .env
web: gunicorn devsite.wsgi --log-file -
