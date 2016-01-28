Atlas Import
============


Requirements
------------

* Python 3 (required)
* Virtualenv (recommended)
* Docker-Compose (recommended)


Developing
----------

Use `docker-compose` to start a local database. Use `sudo` is you're running on Linux.

	docker-compose up -d

Create a new virtual env, and execute the following:

	pip install -r requirements.txt
	export DJANGO_SETTINGS_MODULE=atlas_import.settings.local
	./atlas_import/manage.py migrate
	./atlas_import/manage.py runserver
	

The Atlas import module should now be available on http://localhost:8000/

To run an import, execute:

	./atlas_import/manage.py run_import

To see the various options for partial imports, execute:

	./atlas_import/manage.py run_import --help
	

Importing the latest backup
---------------------------
	
Run `docker-compose` to determine the name of your database image:

	$ docker-compose ps
               Name                          Command               State                       Ports                      
    ---------------------------------------------------------------------------------------------------------------------
    atlasbackend_atlas_1           /bin/sh -c /app/docker-ent ...   Up      0.0.0.0:32772->8080/tcp                        
    atlasbackend_database_1        /docker-entrypoint.sh postgres   Up      0.0.0.0:5434->5432/tcp                         
    atlasbackend_elasticsearch_1   /docker-entrypoint.sh elas ...   Up      0.0.0.0:9200->9200/tcp, 0.0.0.0:9300->9300/tcp 
    
    
In this example, it's `atlasbackend_database_1`. Use that name in the following command (using `sudo` if you're running
on Linux):
    
    docker exec atlasbackend_database_1 update-atlas.sh
     
The import takes approximately 10 minutes. 
	
	
	

    
