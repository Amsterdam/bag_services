FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ARG BAG_OBJECTSTORE_PASSWORD
ENV BAG_OBJECTSTORE_PASSWORD=$BAG_OBJECTSTORE_PASSWORD

EXPOSE 8080

RUN mkdir -p /static \
	&& chown datapunt /static

WORKDIR /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=bag.settings.docker

USER datapunt
COPY bag /app/
COPY .jenkins-import /.jenkins-import/

CMD /app/docker-entrypoint.sh

