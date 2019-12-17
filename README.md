
BAG
============

Basis Administratie Gebouwen
Basis Administratie Gebieden
Basis Administratie Kadaster

This repository contains Django application that serves the BAG (buildings and
addresses), BBGA (areas), BRK (land register) and WKPB (extra municipal
restrictions on real estate use) REST APIs on
[https://api.data.amsterdam.nl](https://api.data.amsterdam.nl).
These APIs are used among other things to power the Data en Informatie portal website
and maps, available on [https://data.amsterdam.nl](https://data.amsterdam.nl)
Precise definitions of abbreviations like BAG and BRK (and how they relate) are
available, in Dutch, on [Stelselpedia](https://www.amsterdam.nl/stelselpedia/).

Note that since these datasets contain non-public data, we will not provide
access to the underlying databases. Using the provided API to access these data
requires extra credentials which are not publicly available.


Requirements
------------

* Python 3 (required)
* Virtualenv (recommended)
* Docker-Compose (recommended)


Developing
----------

Use `docker-compose` to start a local database and Elasticsearch service. Use
`sudo` if you're running on Linux.

	docker-compose up -d --build database elasticsearch

Then, create and activate a new virtual environment in the `.venv` directory:

	python3 -m venv .venv
	source .venv/bin/activate

In this virtual environment, execute the following commands:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=bag.settings.settings
	./bag/manage.py migrate
	./bag/manage.py runserver

The BAG API should now be available on http://localhost:8000/

To run an import, execute:

	export BAG_OBJECTSTORE_PASSWORD=...
	export GOB_OBJECTSTORE_PASSWORD=...

	DIVA_DIR=./data GOB_DIR=./data/gob bag/objectstore/objectstore.py
	./bag/manage.py run_import
	./bag/manage.py elastic_indices --build

To see the various options for partial imports, execute:

	./bag/manage.py run_import --help


Importing the latest backup
---------------------------

To import the latest database from acceptance (replace `<username>` with your
username, assumes your public SSH key is known and you have appropriate level of access.

This command expects the private SSH key to be found in the ~/.ssh T†folder,
in a file with the name datapunt.key (chmod 600):

    docker-compose exec database update-db.sh bag_v11 <username>

To import the latest elastic index from acceptance:

	docker-compose exec elasticsearch clean-el.sh
	docker-compose exec elasticsearch update-el.sh bag_v11 <username>

The database import takes approximately 10 minutes.
The elastic index import takes approximately 5 minutes.

Your own elastic index import takes approximately 2 hours.
To run your own elastic index:

    docker-compose exec bag /app/manage.py run_import --no-import
