FROM python:3
MAINTAINER datapunt@amsterdam.nl

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt && \
	rm /app/requirements.txt && \
	pip3 install uwsgi && \
	useradd --system django && \
	apt-get update && apt-get install -y gdal-bin && apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

VOLUME /app/diva/

USER django
WORKDIR /app/
EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE=atlas_import.settings.docker

COPY atlas_import /app/

CMD /app/docker-entrypoint.sh

