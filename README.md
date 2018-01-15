
BAG
============

Basis Administratie Gebouwen
Basis Administratie Gebieden
Basis Administratie Kadaster

This repository contains Django application that serves the BAG (buildings and
addresses), BBGA (areas), BRK (land register) and WKPB (extra municipal
restrictiond on real estate use) REST APIs on
[https://api.data.amsterdam.nl](https://api.data.amsterdam.nl).
These APIs are used among other things to power the City data portal website
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

Use `docker-compose` to start a local database and Elastic Search service. Use
`sudo` if you're running on Linux.

	docker-compose up -d --build database elasticsearch

Create a new virtual env, and execute the following:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=bag.settings.settings
	./bag/manage.py migrate
	./bag/manage.py runserver


The BAG API should now be available on http://localhost:8000/

To run an import, execute:

	./bag/manage.py run_import
	./bag/manage.py elastic_indices --build

To see the various options for partial imports, execute:

	./bag/manage.py run_import --help


Importing the latest backup
---------------------------

To import the latest database from acceptance (replace `<username>` with your
username, assumes your SSH key is known and you have appropriate level of access):

    docker-compose exec database update-db.sh bag <username>

To import the latest elastic index from acceptance:

 	make sure LOCAL=true as environment variable

	docker-compose exec elasticsearch update-el.sh bag bag*,brk*,nummeraanduiding

The database import takes approximately 10 minutes.
The elastic index import takes approximately 5 minutes.

Your own elastic index import takes approximately 2 hours.
To run your own elastic index:

    docker-compose exec bag /app/manage.py run_import --no-import
