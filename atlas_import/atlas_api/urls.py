from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views
import datasets.bag.views
import datasets.akr.views
import datasets.wkpb.views


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
router.register(r'bag/ligplaats', datasets.bag.views.LigplaatsViewSet)
router.register(r'bag/standplaats', datasets.bag.views.StandplaatsViewSet)
router.register(r'bag/verblijfsobject', datasets.bag.views.VerblijfsobjectViewSet)
router.register(r'bag/openbareruimte', datasets.bag.views.OpenbareRuimteViewSet)
router.register(r'bag/nummeraanduiding', datasets.bag.views.NummeraanduidingViewSet)
router.register(r'bag/pand', datasets.bag.views.PandViewSet)
router.register(r'kadaster/subject', datasets.akr.views.KadastraalSubjectViewSet)
router.register(r'kadaster/object', datasets.akr.views.KadastraalObjectViewSet)
router.register(r'kadaster/transactie', datasets.akr.views.TransactieViewSet)
router.register(r'kadaster/zakelijk-recht', datasets.akr.views.ZakelijkRechtViewSet)
router.register(r'wkpb/beperking', datasets.wkpb.views.BeperkingView)

router.register(r'atlas/typeahead', views.TypeaheadViewSet, base_name='typeahead')
router.register(r'atlas/search', views.SearchViewSet, base_name='search')

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
