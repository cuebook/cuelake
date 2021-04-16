#!/usr/bin/env bash
# start-server.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --no-input)
fi
export DEBUG=false
python manage.py migrate
python manage.py loaddata seeddata/*.json
chmod -R 777 db
chown -R www-data:www-data db
(gunicorn app.wsgi --user www-data --bind 0.0.0.0:8000 --workers 3) &
(celery -A app worker --concurrency=25 -l INFO) &
(celery -A app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler)
nginx -g "daemon off;"