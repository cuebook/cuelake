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
(uvicorn app.asgi:application --lifespan on) &
(celery -A app worker --concurrency=500 -P gevent -l INFO --purge) &
(celery -A app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler) &
nginx -g "daemon off;"
