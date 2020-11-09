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

from django.conf import settings
from django.conf.urls import url, include
from rest_framework import renderers, schemas, response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

from django.conf.urls.static import static

import search.urls
import bag.urlsets

grouped_url_patterns = {
    'base_patterns': [
        url(r'^status/', include('health.urls')),
    ],

    'bag_patterns': [
        url(r'^bag/v1.1/', include(bag.urlsets.bag.urls)),
    ],

    'gebieden_patterns': [
        url(r'^gebieden/', include(bag.urlsets.gebieden.urls)),
    ],

    'brk_patterns': [
        url(r'^brk/', include(bag.urlsets.brk.urls)),
    ],

    'typeahead_patterns': [
        # atlas is depricated
        url(r'^atlas/typeahead/', include(search.urls.typeahead.urls)),
        # url(r'^typeahead/', include(search.urls.typeahead.urls)),
    ],

    'search_patterns': [
        # atlas is depricated
        url(r'^atlas/search/', include(search.urls.bag_search.urls)),
        # url(r'^search/', include(search.urls.bag_search.urls)),
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


urlpatterns = []


if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )


urlpatterns.extend(
    [
        url('^bag/v1.1/docs/api-docs/bag/$', bag_schema_view),
        url('^bag/docs/api-docs/bag/$', bag_schema_view),
        url('^bag/docs/api-docs/gebieden/$', gebieden_schema_view),
        url('^bag/docs/api-docs/brk/$', brk_schema_view),
        url('^bag/docs/api-docs/pcsearch/$', postcode_schema_view),
        url('^bag/docs/api-docs/search/$', search_schema_view),
        url('^bag/docs/api-docs/typeahead/$', typeahead_schema_view),
    ] + [p_url for pattern_list in grouped_url_patterns.values()
         for p_url in pattern_list])

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
