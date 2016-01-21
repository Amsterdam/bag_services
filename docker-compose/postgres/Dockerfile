FROM postgres:9.3

RUN apt-get update \
	&& apt-get install -y postgresql-9.3-postgis-scripts wget \
	&& rm -rf /var/lib/apt/lists/*

COPY atlas-update.sh /
RUN chmod 700 /atlas-update.sh