# How to Runserver

ps: this guide was made inside a arch environment and assumes that you already have docker and postgres related librarys installed.

Iniciate docker.service:

    sudo systemctl start docker

Go to the directory where the database will settle:

    cd server-medications/dbms

Start the docker container:

    sudo docker-compose -f docker-compose-model.yml up -d

(Optional to check if docker service is running)

    sudo docker ps

Now that the docker service is running on background, we need to navigate into the directory with the "manage.py" file:

    cd server-medications/lembramed

Activate the virtual environment:

    source venv/bin/activate

Dowload the project dependencies:

    pip install -r ../requirements.txt

Create the tables and conect them to the dataset:

    python manage.py makemigrations
    python manage.py migrate

Create a superuser to acess admin permissions:

    python manage.py createsuperuser

Initiates the service:

    python manage.py runserver

# Utilities

To have acess to our pre established medication and leaflets data, first enter the directory with 'manage.py' file:

    cd server-medications/lembramed

And then, after running "makemigrations" and "migrate" run these commands:

    python manage.py load_bula_data
    python manage.py load_medications_data

You should see sucess messages on terminal.

# Quick Web Links to Test Server

- Frontend: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/
- API Testing: http://127.0.0.1:8000/api/docs/

Common Errors

If you already had started the docker container, it will be needed for you to end their activity before starting them again:

    cd server-medications/dbms
    sudo docker compose -f docker-compose-model.yml down -v

If there`s data conflict locally, located in server-medications/dbms/data, it will be needed to restart that database:

    cd server-medications/dbms
    sudo rm -rf data
    sudo docker-compose -f docker-compose-model.yml up -d --build

If there`s a psycopg2 error involved when trying to pip install, it indicates that you do not have postgresql and needed libs downloaded locally. Quit the virtual environment and run:

    sudo pacman -S postgresql postgis postgresql-docs

If you cant pip install, even though you have pip installed in your machine, verify your pip`s path inside the virtual environment:

    which pip
    # if something like "usr/bin..." appears, go to the "manage.py" directory (server-medications/lembramed) and:
    sudo rm -rf venv # delete your old venv directory
    python -m venv venv # create another one
    # Now activate again the virtual environment, it should work just fine.
