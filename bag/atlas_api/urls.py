from rest_framework import routers

import datasets.bag.views
import datasets.brk.views
import datasets.wkpb.views
from atlas_api import views


class SearchRouter(routers.DefaultRouter):
    """
    Search

    End point for different search uris, offering data not directly reflected in the models
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Search(cls):
            pass

        Search.__doc__ = self.__doc__
        return Search.as_view()


class BagRouter(routers.DefaultRouter):
    """
    BAG.

    De [Basisregistraties adressen en gebouwen (BAG)](http://www.amsterdam.nl/stelselpedia/bag-index/)
    bevatten gegevens over panden, verblijfsobjecten, standplaatsen en
    ligplaatsen en de bijbehorende adressen en de benoeming van
    woonplaatsen en openbare ruimten.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class BAG(cls):
            pass

        BAG.__doc__ = self.__doc__
        return BAG.as_view()


class GebiedenRouter(routers.DefaultRouter):
    """
    Gebieden

    In de [Registratie gebieden](https://www.amsterdam.nl/stelselpedia/gebieden-index/)
    worden de Amsterdamse stadsdelen, buurtcombinaties, buurten en bouwblokken vastgelegd. Verder bevat de
    registratie gegevens van de grootstedelijke gebieden binnen de gemeente, de UNESCO werelderfgoedgrens en de
    gebieden van gebiedsgericht werken.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Gebieden(cls):
            pass

        Gebieden.__doc__ = self.__doc__
        return Gebieden.as_view()


class BrkRouter(routers.DefaultRouter):
    """
    BRK Basisregistratie kadaster

    De [Basisregistratie kadaster (BRK)](https://www.amsterdam.nl/stelselpedia/brk-index/)
    bevat informatie over percelen, eigendom, hypotheken, beperkte rechten (zoals recht van erfpacht, opstal en
    vruchtgebruik) en leidingnetwerken. Daarnaast staan er kadastrale kaarten in met perceel, perceelnummer,
    oppervlakte, kadastrale grens en de grenzen van het rijk, de provincies en gemeenten.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class BRK(cls):
            pass

        BRK.__doc__ = self.__doc__
        return BRK.as_view()


class WkpbRouter(routers.DefaultRouter):
    """
    Wkpd

    De [Gemeentelijke beperkingenregistratie op grond van de Wkpb](https://www.amsterdam.nl/stelselpedia/wkpb-index/)
    bevat alle bij wet genoemde beperkingenbesluiten op onroerende
    zaken, die het gemeentebestuur heeft opgelegd.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class WKPB(cls):
            pass

        WKPB.__doc__ = self.__doc__
        return WKPB.as_view()


class AtlasRouter(routers.DefaultRouter):
    """
    Specifieke functionaliteit voor de Atlas API.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class Atlas(cls):
            pass

        Atlas.__doc__ = self.__doc__
        return Atlas.as_view()


bag = BagRouter()
bag.register(r'ligplaats', datasets.bag.views.LigplaatsViewSet)
bag.register(r'standplaats', datasets.bag.views.StandplaatsViewSet)

bag.register(r'verblijfsobject', datasets.bag.views.VerblijfsobjectViewSet)

bag.register(r'openbareruimte', datasets.bag.views.OpenbareRuimteViewSet)
bag.register(r'nummeraanduiding', datasets.bag.views.NummeraanduidingViewSet)
bag.register(r'pand', datasets.bag.views.PandViewSet)
bag.register(r'woonplaats', datasets.bag.views.WoonplaatsViewSet)

gebieden = GebiedenRouter()
gebieden.register(r'stadsdeel', datasets.bag.views.StadsdeelViewSet)
gebieden.register(r'buurt', datasets.bag.views.BuurtViewSet)
gebieden.register(r'bouwblok', datasets.bag.views.BouwblokViewSet)

gebieden.register(
    r'buurtcombinatie', datasets.bag.views.BuurtcombinatieViewSet)
gebieden.register(
    r'gebiedsgerichtwerken', datasets.bag.views.GebiedsgerichtwerkenViewSet)
gebieden.register(
    r'grootstedelijkgebied', datasets.bag.views.GrootstedelijkgebiedViewSet)
gebieden.register(r'unesco', datasets.bag.views.UnescoViewSet)

brk = BrkRouter()
brk.register(r'gemeente', datasets.brk.views.GemeenteViewSet)

brk.register(
    r'kadastrale-gemeente', datasets.brk.views.KadastraleGemeenteViewSet)

brk.register(r'kadastrale-sectie', datasets.brk.views.KadastraleSectieViewSet)
brk.register(r'subject', datasets.brk.views.KadastraalSubjectViewSet)

brk.register(r'object', datasets.brk.views.KadastraalObjectViewSet)

brk.register(r'object-expand',
             datasets.brk.views.KadastraalObjectViewSetExpand,
             base_name='object-expand',
             )

brk.register(r'zakelijk-recht', datasets.brk.views.ZakelijkRechtViewSet)
brk.register(r'aantekening', datasets.brk.views.AantekeningViewSet)

wkpb = WkpbRouter()
wkpb.register(r'beperking', datasets.wkpb.views.BeperkingView)
wkpb.register(r'brondocument', datasets.wkpb.views.BrondocumentView)
wkpb.register(r'broncode', datasets.wkpb.views.BroncodeView)

atlas = AtlasRouter()

# Search related

atlas.register(r'typeahead', views.TypeaheadViewSet, base_name='typeahead')

# Alias voor nummeraanduiding
atlas.register(
    r'search/adres',
    views.SearchNummeraanduidingViewSet, base_name='search/adres')
atlas.register(
    r'search/bouwblok',
    views.SearchBouwblokViewSet, base_name='search/bouwblok')
atlas.register(
    r'search/kadastraalsubject',
    views.SearchSubjectViewSet, base_name='search/kadastraalsubject')
atlas.register(
    r'search/postcode',
    views.SearchPostcodeViewSet, base_name='search/postcode')
atlas.register(
    r'search/kadastraalsubject',
    views.SearchSubjectViewSet, base_name='search/kadastraalsubject')
atlas.register(
    r'search/kadastraalobject',
    views.SearchObjectViewSet, base_name='search/kadastraalobject')

atlas.register(
    r'search/openbareruimte',
    views.SearchOpenbareRuimteViewSet, base_name='search/openbareruimte')

search = SearchRouter()
search.register(
    r'postcode', views.SearchExactPostcodeToevoegingViewSet,
    base_name='postcode')

urlpatterns = [
    # url(r'^gebieden/bouwblok/(?P<code>....)/?$',
    #    datasets.bag.views.BouwblokCodeView.as_view()),
]
