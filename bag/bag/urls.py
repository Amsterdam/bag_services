"""BAG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import renderers, schemas, response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

import atlas_api.urls
import batch.views as b_views
import datasets.bag.views
import datasets.brk.views

grouped_url_patterns = {
    'base_patterns': [
        url(r'^jobs/?$', b_views.JobListView.as_view(), name='job-list'),
        url(r'^jobs/(?P<pk>.*)$', b_views.JobDetailView.as_view(),
            name='job-detail'),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^oauth/',
            include('oauth2_provider.urls', namespace='oauth2_provider')),
        url(r'^status/', include('health.urls', namespace='health')),
    ],

    'bag_patterns': [
        url(r'^bag/', include(atlas_api.urls.bag.urls)),
    ],

    'gebieden_patterns': [
        url(r'^gebieden/bouwblok/(?P<code>....)/?$',
            datasets.bag.views.BouwblokCodeView.as_view()),
        url(r'^gebieden/stadsdeel/(?P<code>.)/?$',
            datasets.bag.views.StadsdeelCodeView.as_view()),
        url(r'^gebieden/',
            include(atlas_api.urls.gebieden.urls)),
    ],

    'brk_patterns': [
        url(r'^brk/', include(atlas_api.urls.brk.urls)),
        url(r'^brk/object-wkpb/(?P<pk>[^/]+)/?$',
            datasets.brk.views.KadastraalObjectWkpbView.as_view(),
            name='brk-object-wkpb'),
    ],

    'beperkingen_patterns': [
        url(r'^wkpb/', include(atlas_api.urls.wkpb.urls)),
    ],

    'postcode_patterns': [
        url(r'^search/', include(atlas_api.urls.search.urls)),
    ],

    'typeahead_patterns': [
        url(r'^atlas/typeahead/', include(atlas_api.urls.typeahead.urls)),
    ],

    'search_patterns': [
        url(r'^atlas/search/', include(atlas_api.urls.bag_search.urls)),
    ],
}


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def bag_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='BAG API',
        patterns=grouped_url_patterns['bag_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def gebieden_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Gebieden API',
        patterns=grouped_url_patterns['gebieden_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def brk_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='BRK API',
        patterns=grouped_url_patterns['brk_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def wkpb_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='WKPB API',
        patterns=grouped_url_patterns['beperkingen_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def postcode_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Postcode API',
        patterns=grouped_url_patterns['postcode_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def typeahead_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Typeahead APIs',
        patterns=grouped_url_patterns['typeahead_patterns']
    )
    return response.Response(generator.get_schema(request=request))


@api_view()
@renderer_classes(
    [SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def search_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='Search APIs',
        patterns=grouped_url_patterns['search_patterns']
    )
    return response.Response(generator.get_schema(request=request))


urlpatterns = [
                  url('^bag/docs/api-docs/bag/$', bag_schema_view),
                  url('^bag/docs/api-docs/gebieden/$', gebieden_schema_view),
                  url('^bag/docs/api-docs/brk/$', brk_schema_view),
                  url('^bag/docs/api-docs/wkpb/$', wkpb_schema_view),
                  url('^bag/docs/api-docs/pcsearch/$', postcode_schema_view),
                  url('^bag/docs/api-docs/search/$', search_schema_view),
                  url('^bag/docs/api-docs/typeahead/$', typeahead_schema_view),
              ] + [url for pattern_list in grouped_url_patterns.values()
                   for url in pattern_list]
