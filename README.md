# Data Science for Citizens
# Server Application Software

This project embraces the server implementation for the medications app.

## Directory Structure

* `install` - installation instructions of the PostgreSQL in docker plus the SQLModel and FastAPI libraries;
* `model` - schemas and diagrams of the data model;
* `src` - server source code in Python.

## Running the Main Server Application

rename the .env_model.py to just .env and replace the placeholders with the actual information before running

~~~
fastapi dev main_common.py
~~~