"""atlas_import URL Configuration

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
import atlas_api.urls
import datasets.bag.views
import datasets.brk.views

import batch.views as b_views

urlpatterns = [
    # custom endpoints
    url(r'^gebieden/bouwblok/(?P<code>....)/?$',
        datasets.bag.views.BouwblokCodeView.as_view()),

    url(r'^gebieden/stadsdeel/(?P<code>.)/?$',
        datasets.bag.views.StadsdeelCodeView.as_view()),

    url(r'^brk/object-wkpb/(?P<pk>[^/]+)/?$',
        datasets.brk.views.KadastraalObjectWkpbView.as_view(),
        name='brk-object-wkpb'),

    #url(r'^bag/nummeraanduiding-expanded/(?P<pk>[^/]+)/?$',
    #    datasets.bag.views.NummerAanduidingExpandedView.as_view(),
    #    name='bag-nummeraanduiding-expanded'),

    #url(r'^bag/verblijfsobject-expanded/(?P<pk>[^/]+)/$',
    #    datasets.bag.views.VerblijfsobjectExpandedView.as_view(),
    #    name='bagverblijfsobjectexpanded'),

    url(r'^bag/docs/', include('rest_framework_swagger.urls')),

    url(r'^bag/', include(atlas_api.urls.bag.urls)),
    url(r'^gebieden/', include(atlas_api.urls.gebieden.urls)),
    url(r'^brk/', include(atlas_api.urls.brk.urls)),
    url(r'^wkpb/', include(atlas_api.urls.wkpb.urls)),
    url(r'^atlas/', include(atlas_api.urls.atlas.urls)),
    url(r'^search/', include(atlas_api.urls.search.urls)),

    url(r'^jobs/?$', b_views.JobListView.as_view(), name='job-list'),
    url(r'^jobs/(?P<pk>.*)$',
        b_views.JobDetailView.as_view(), name='job-detail'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth/',
        include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^status/', include('health.urls', namespace='health')),
]
