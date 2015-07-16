FROM postgres:9.3

RUN apt-get update \
	&& apt-get install -y postgresql-9.3-postgis-scripts \
	&& rm -rf /var/lib/apt/lists/*
