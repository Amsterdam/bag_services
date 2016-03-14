Atlas import
============

# Abstract

This project contains the python/django code for importing the following DIVA datasets for Atlas:

- BAG
- BRK
- Gebieden
- LKI
- WKPB

The datasets are accessable via an API, structured as defined on [stelselpedia](https://www.amsterdam.nl/stelselpedia/). This is implemented using Django rest-framework (DRF). Some datasets are also searchable, currently this is done using elasticsearch.

Database views for mapserver usage are also available.

# Application layout

The application consists of the following django apps:

## atlas

This app contains management commands for executing import tasks and managing the elasticsearch indices.

## atlas_api

This app contains top-level code for the project (REST) API. Search viewsets are defined here, and all viewsets from the datasets modules are included here in urls.py to expose all endpoints. Tests for the API and search endpoints are also in this app.

Management commands regarding the API are also located here.

## atlas_import

This app contains project settings, main urls.py and the wsgi application.

## batch

Batch is generic module for handling import tasks.

## datasets

The datasets app contains all modules for importing the different datasets. Each module contains:

- model definitions
- batch script where all import tasks are defined
- viewsets for the API
- model serializers
- elasticsearch document definitions (optional)

### Serializers

Serializing models is using an extended [HyperlinkedModelSerializer](http://www.django-rest-framework.org/tutorial/5-relationships-and-hyperlinked-apis/). This is interesting the because the normal way of including a related model was handled very poorly at least.

Basically there's two kinds of serializers for a model: a detail one, and a list one. In stead of including all related models int the serializer, a link is added to be able to fetch them when needed.


-- ga niet haten ik ben bezig
