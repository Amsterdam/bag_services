from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views

router = routers.DefaultRouter()
router.register(r'ligplaatsen', views.LigplaatsViewSet)
router.register(r'standplaatsen', views.StandplaatsViewSet)
router.register(r'verblijfsobjecten', views.VerblijfsobjectViewSet)
router.register(r'nummeraanduidingen', views.NummeraanduidingViewSet)
router.register(r'panden', views.PandViewSet)

urlpatterns = [
    url(r'^typeahead$', views.TypeaheadView.as_view()),
    url(r'^', include(router.urls)),
]