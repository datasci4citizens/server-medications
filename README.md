# How to Runserver

ps: this guide was made inside a arch environment and assumes that you already have docker and postgres related librarys installed.

Iniciate docker.service:

```bash
sudo systemctl start docker
```

Go to the directory where the database will settle:

```bash
cd server-medications/dbms
```

Start the docker container:

```bash
docker compose -f docker-compose.yml up -d
```

(Optional to check if docker service is running)

```bash
sudo docker ps
```

Now that the docker service is running on background, we need to navigate into the directory with the "manage.py" file:

```bash
cd server-medications/lembramed
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Dowload the project dependencies:

```bash
pip install -r ../requirements.txt
```

Create the tables and conect them to the dataset:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Create a superuser to acess admin permissions:

```bash
python3 manage.py createsuperuser
```

Initiates the service:

```bash
python3 manage.py runserver
```

# Utilities

To have acess to our pre established 10745 medication and 7730 leaflets data, first enter the directory with 'manage.py' file:

```bash
cd server-medications/lembramed
```

And then, after running "makemigrations" and "migrate" run this commands:

```bash
python3 manage.py load_medications_data
```

For accessing the beta database, with 60 medications/leaflets, run:

```bash
python3 manage.py load_beta
```

You should see success messages on ther terminal.

# Quick Web Links to Test Server

- Admin Panel: http://127.0.0.1:8000/admin/
- API Testing: http://127.0.0.1:8000/api/docs/

# Common Errors

If you already had started the docker container, it will be needed for you to end their activity before starting them again:

```bash
cd server-medications/dbms
sudo docker compose -f docker-compose-model.yml down -v
```

If there`s data conflict locally, located in server-medications/dbms/data, it will be needed to restart that database:

```bash
cd server-medications/dbms
sudo rm -rf data
sudo docker-compose -f docker-compose-model.yml up -d --build
```

If there`s a psycopg2 error involved when trying to pip install, it indicates that you do not have postgresql and needed libs downloaded locally. Quit the virtual environment and run:

```bash
sudo pacman -S postgresql postgis postgresql-docs
```

If you cant pip install, even though you have pip installed in your machine, verify your pip`s path inside the virtual environment:

```bash
which pip
# if something like "usr/bin..." appears, go to the "manage.py" directory (server-medications/lembramed) and:
sudo rm -rf venv # delete your old venv directory
python3 -m venv venv # create another one
# Now activate again the virtual environment, it should work just fine.
```

To revert some already made migrations on a django app named 'X':

```bash
# Run this command inside the directory with the "manage.py" file
python3 manage.py migrate X zero
```