from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views
import bag.views

router = routers.DefaultRouter()
router.register(r'ligplaatsen', bag.views.LigplaatsViewSet)
router.register(r'standplaatsen', bag.views.StandplaatsViewSet)
router.register(r'verblijfsobjecten', bag.views.VerblijfsobjectViewSet)
router.register(r'nummeraanduidingen', bag.views.NummeraanduidingViewSet)
router.register(r'panden', bag.views.PandViewSet)
router.register(r'typeahead', views.TypeaheadViewSet, base_name='typeahead')

urlpatterns = [
    url(r'^', include(router.urls)),
]