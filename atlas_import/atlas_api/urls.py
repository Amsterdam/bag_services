from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views
import datasets.bag.views

class DocumentedRouter(routers.DefaultRouter):
    """
    Onderstaande lijst bevat alle API's die door Datapunt zelf worden geleverd.

    `bag/`
    :   [Basisadministratie Adressen en Gebouwen](http://www.amsterdam.nl/stelselpedia/bag-index/)

    `atlas/`
    :   Specifieke functionaliteit voor Atlas
    """

    def get_api_root_view(self):
        view = super().get_api_root_view()
        cls = view.cls

        class Datapunt(cls):
            pass

        Datapunt.__doc__ = self.__doc__
        return Datapunt.as_view()


router = DocumentedRouter()
router.register(r'bag/ligplaatsen', datasets.bag.views.LigplaatsViewSet)
router.register(r'bag/standplaatsen', datasets.bag.views.StandplaatsViewSet)
router.register(r'bag/verblijfsobjecten', datasets.bag.views.VerblijfsobjectViewSet)
router.register(r'bag/openbareruimtes', datasets.bag.views.OpenbareRuimteViewSet)
router.register(r'bag/nummeraanduidingen', datasets.bag.views.NummeraanduidingViewSet)
router.register(r'bag/panden', datasets.bag.views.PandViewSet)

router.register(r'atlas/typeahead', views.TypeaheadViewSet, base_name='typeahead')
router.register(r'search', views.SearchViewSet, base_name='search')

urlpatterns = [
    url(r'^', include(router.urls)),
]