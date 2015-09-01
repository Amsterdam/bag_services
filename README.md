Atlas Import
============


Requirements
------------

* Python 3 (required)
* Virtualenv (recommended)
* Docker-Compose (recommended)


Developing
----------

User `docker-compose` to start a local database. 

	docker-compose start


Create a new virtual env, and execute the following:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=atlas_import.settings.local
	./atlas_import/manage.py migrate
	./atlas_import/manage.py runserver
	

The Atlas import module should now be available on http://localhost:8000/

To run an import, execute:

	./atlas_import/manage.py run_import
	
