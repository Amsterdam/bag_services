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

	docker-compose up -d

Create a new virtual env, and execute the following:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=bag.settings.local
	./bag/manage.py migrate
	./bag/manage.py runserver


The Atlas import module should now be available on http://localhost:8000/

To run an import, execute:

	./bag/manage.py run_import

To see the various options for partial imports, execute:

	./bag/manage.py run_import --help


Importing the latest backup
---------------------------

Run `docker-compose` to determine the name of your database image:

	$ docker-compose ps
               Name                          Command               State                       Ports
    ---------------------------------------------------------------------------------------------------------------------
    atlasbackend_atlas_1           /bin/sh -c /app/docker-ent ...   Up      0.0.0.0:32772->8080/tcp
    atlasbackend_database_1        /docker-entrypoint.sh postgres   Up      0.0.0.0:5434->5432/tcp
    atlasbackend_elasticsearch_1   /docker-entrypoint.sh elas ...   Up      0.0.0.0:9200->9200/tcp, 0.0.0.0:9300->9300/tcp


In this example, it's `atlasbackend_database_1`. Use that name in the following command:

    docker-compose pull
    docker-compose build
    docker-compose up -d

To import the latest database from acceptance:

    docker exec -it atlasbackend_database_1 update-atlas.sh

To import the latest elastic index from acceptance:

	docker exec -it $(docker-compose ps -q elasticsearch) update-atlas.sh

The database import takes approximately 10 minutes.
The elastic index import takes approximately 5 minutes.

Your own elastic index import takes approximately 2 hours.
To run your own elastic index:

    docker exec -it atlasbackend_atlas_1 /app/manage.py run_import --no-import

test
