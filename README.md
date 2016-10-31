BAG
============

Basis Administratie Gebouwen
Basis Administratie Gebieden
Basis Administratie Kadaster

BAG of stuff.


Requirements
------------

* Python 3 (required)
* Virtualenv (recommended)
* Docker-Compose (recommended)


Developing
----------

Use `docker-compose` to start a local database. Use `sudo` if you're running on Linux.

	docker-compose up -d --build

Create a new virtual env, and execute the following:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=bag.settings.docker
	./bag/manage.py migrate
	./bag/manage.py runserver


The Atlas import module should now be available on http://localhost:8000/

To run an import, execute:

	./bag/manage.py run_import

To see the various options for partial imports, execute:

	./bag/manage.py run_import --help


Importing the latest backup
---------------------------

To import the latest database from acceptance:

    docker-compose exec database update-db.sh atlas

To import the latest elastic index from acceptance:

	docker-compose exec elasticsearch update-atlas.sh

The database import takes approximately 10 minutes.
The elastic index import takes approximately 5 minutes.

Your own elastic index import takes approximately 2 hours.
To run your own elastic index:

    docker-compose exec atlas /app/manage.py run_import --no-import
