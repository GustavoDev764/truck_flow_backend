#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "PostgreSQL disponível."

echo "Executando migrações..."
python manage.py migrate --noinput

echo "Criando grupos e usuários de exemplo..."
python manage.py seed_groups --create-users

if [ -n "$SUPERUSER_USERNAME" ] && [ -n "$SUPERUSER_EMAIL" ] && [ -n "$SUPERUSER_PASSWORD" ]; then
  echo "Criando superusuário..."
  DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD" python manage.py createsuperuser \
    --noinput --username "$SUPERUSER_USERNAME" --email "$SUPERUSER_EMAIL" || echo "Superusuário já existe ou erro ao criar."
fi

echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:${HOST_PORT:-3000}
