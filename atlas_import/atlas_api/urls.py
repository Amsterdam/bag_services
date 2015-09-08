from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views
import bag.views

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
router.register(r'bag/ligplaatsen', bag.views.LigplaatsViewSet)
router.register(r'bag/standplaatsen', bag.views.StandplaatsViewSet)
router.register(r'bag/verblijfsobjecten', bag.views.VerblijfsobjectViewSet)
router.register(r'bag/nummeraanduidingen', bag.views.NummeraanduidingViewSet)
router.register(r'bag/panden', bag.views.PandViewSet)

router.register(r'atlas/typeahead', views.TypeaheadViewSet, base_name='typeahead')

urlpatterns = [
    url(r'^', include(router.urls)),
]