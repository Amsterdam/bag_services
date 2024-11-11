FROM python:3.9-bullseye as builder
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install --no-install-recommends -y \
    curl \
    gdal-bin \
    libgeos-c1v5 \
    libpq5 \
    netcat-openbsd \
    build-essential \
    libgeos-dev \
    libpq-dev \
    python3-dev \
    libffi-dev

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Start runtime image
FROM python:3.9-bullseye
RUN apt update && apt install --no-install-recommends -y \
    gdal-bin \
    libgeos-c1v5 \
    libpq5 \
    netcat-openbsd 

# Copy python build artifacts from builder image
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

RUN adduser --system datapunt


ENV PYTHONUNBUFFERED 1
ARG BAG_OBJECTSTORE_PASSWORD
ENV BAG_OBJECTSTORE_PASSWORD=$BAG_OBJECTSTORE_PASSWORD


WORKDIR /app/

RUN chown datapunt -R /app
EXPOSE 8080


RUN mkdir -p /static && chown datapunt /static

ENV DJANGO_SETTINGS_MODULE=bag.settings.docker

COPY bag /app/
COPY .jenkins-import /.jenkins-import/

USER datapunt

ENV BAG_SECRET_KEY=insecure
RUN ./manage.py collectstatic

CMD /app/docker-entrypoint.sh
