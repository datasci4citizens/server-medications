# PostgreSQL
https://www.postgresql.org

# PostgreSQL Docker

Image: https://hub.docker.com/_/postgres

The `docker-compose.yml` has the instructions for "docker compose":

* It departs from the Postgres Docker image.
* It is meant to be a local configuration of the docker image and must be adapted to the deployment server.
* In the `ports` section, it exposes the default Postgres port (`5432`).
* It maps two internal (docker machine) folders to external (host machine) ones.
  * The default internal docker database folder (`/var/lib/postgresql/data`) is mapped to the external: `/home/user/data/pgsql/docker`.
  * The internal home directory (`/home`) is mapped to the external: `/home/user/data/pgsql/impexp`. This directory is meant to manage files imported/exported.
  * You must adjust the external directory to your machine folder structure.
* The `restart` clause considers the local dev environment (it does not restart whenever you turn the machine on). In the server configuration, we suggest replacing it with `restart: always`.

To run:
~~~
docker compose up
~~~

# Interaction

~~~
docker exec -it 1-postgresql-db-1 bash
psql -U postgres citizen
~~~
