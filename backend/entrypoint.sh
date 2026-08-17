#!/bin/sh
set -e

echo "Waiting for postgres..."
while ! python -c "import socket,os; s=socket.socket(); s.settimeout(1); s.connect((os.environ.get('POSTGRES_HOST','db'), int(os.environ.get('POSTGRES_PORT','5432'))))" 2>/dev/null; do
  sleep 1
done
echo "Postgres is up."

python manage.py migrate --noinput
python manage.py seed_demo
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
