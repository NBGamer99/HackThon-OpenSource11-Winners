rm db.sqlite3
rm ./Home/migrations/0*

python manage.py flush

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

