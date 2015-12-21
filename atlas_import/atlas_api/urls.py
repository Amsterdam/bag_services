from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers
from atlas_api import views
import datasets.bag.views
import datasets.akr.views
import datasets.wkpb.views
import datasets.brk.views


class DocumentedRouter(routers.DefaultRouter):
    """
    Onderstaande lijst bevat alle API's die door Datapunt zelf worden geleverd.

    `bag/`
    :   [Basisadministratie Adressen en Gebouwen](http://www.amsterdam.nl/stelselpedia/bag-index/)

    `gebieden/`
    :   [Registratie gebieden](https://www.amsterdam.nl/stelselpedia/gebieden-index/)

    `brk/`
    :   [Basisregistratie kadaster](https://www.amsterdam.nl/stelselpedia/brk-index/)

    `wkpb/`
    :   [Gemeentelijke beperkingenregistratie](https://www.amsterdam.nl/stelselpedia/wkpb-index/)

    `brk/`
    :   [Basisregistratie kadaster (vanaf 1-1-2016)](https://www.amsterdam.nl/stelselpedia/brk-index/catalog-brk-levering/)

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
router.register(r'bag/woonplaats', datasets.bag.views.WoonplaatsViewSet)

router.register(r'gebieden/stadsdeel', datasets.bag.views.StadsdeelViewSet)
router.register(r'gebieden/buurt', datasets.bag.views.BuurtViewSet)
router.register(r'gebieden/bouwblok', datasets.bag.views.BouwblokViewSet)
router.register(r'gebieden/buurtcombinatie', datasets.bag.views.BuurtcombinatieViewSet)
router.register(r'gebieden/gebiedsgerichtwerken', datasets.bag.views.GebiedsgerichtwerkenViewSet)
router.register(r'gebieden/grootstedelijkgebied', datasets.bag.views.GrootstedelijkgebiedViewSet)
router.register(r'gebieden/unesco', datasets.bag.views.UnescoViewSet)

router.register(r'brk/gemeente', datasets.brk.views.GemeenteViewSet)
router.register(r'brk/kadastrale-gemeente', datasets.brk.views.KadastraleGemeenteViewSet)
router.register(r'brk/kadastrale-sectie', datasets.brk.views.KadastraleSectieViewSet)
router.register(r'brk/subject', datasets.brk.views.KadastraalSubjectViewSet)
router.register(r'brk/object', datasets.brk.views.KadastraalObjectViewSet)
router.register(r'brk/zakelijk-recht', datasets.brk.views.ZakelijkRechtViewSet)
router.register(r'brk/aantekening', datasets.brk.views.AantekeningViewSet)

router.register(r'wkpb/beperking', datasets.wkpb.views.BeperkingView)
router.register(r'wkpb/brondocument', datasets.wkpb.views.BrondocumentView)
router.register(r'wkpb/broncode', datasets.wkpb.views.BroncodeView)

router.register(r'atlas/typeahead', views.TypeaheadViewSet, base_name='typeahead')
router.register(r'atlas/search', views.SearchViewSet, base_name='search')

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
