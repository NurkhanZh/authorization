echo "going migrations"
python manage.py migrate

echo "start server"
python manage.py runserver 0.0.0.0:8000