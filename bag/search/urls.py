from rest_framework import routers

import datasets.bag.views
import datasets.brk.views

from search import views


class SearchView(routers.APIRootView):
    """
    Search

    End point for different search uris, offering data not directly reflected
    in the models
    """


class SearchRouter(routers.DefaultRouter):
    APIRootView = SearchView


class BagView(routers.APIRootView):
    """
    BAG.

    De [Basisregistraties adressen en gebouwen (BAG)](http://www.amsterdam.nl/stelselpedia/bag-index/)
    bevatten gegevens over panden, verblijfsobjecten, standplaatsen en
    ligplaatsen en de bijbehorende adressen en de benoeming van
    woonplaatsen en openbare ruimten.
    """  # noqa


class BagRouter(routers.DefaultRouter):
    APIRootView = BagView


class GebiedenView(routers.APIRootView):
    """
    Gebieden

    In de [Registratie gebieden](https://www.amsterdam.nl/stelselpedia/gebieden-index/) worden de
    Amsterdamse stadsdelen,
    wijk (voorheen) buurtcombinaties, buurten en bouwblokken
    vastgelegd. Verder bevat de registratie gegevens van de grootstedelijke
    gebieden binnen de gemeente, de UNESCO werelderfgoedgrens en de gebieden
    van gebiedsgericht werken.  """  # noqa


class GebiedenRouter(routers.DefaultRouter):
    APIRootView = GebiedenView


class BrkView(routers.APIRootView):
    """
    BRK Basisregistratie kadaster

    De [Basisregistratie kadaster (BRK)](https://www.amsterdam.nl/stelselpedia/brk-index/)
    bevat informatie over percelen, eigendom, hypotheken, beperkte rechten
    (zoals recht van erfpacht, opstal en vruchtgebruik) en leidingnetwerken.
    Daarnaast staan er kadastrale kaarten in met perceel, perceelnummer,
    oppervlakte, kadastrale grens en de grenzen van het rijk, de provincies en
    gemeenten.
    """  # noqa


class BrkRouter(routers.DefaultRouter):
    APIRootView = BrkView


class TypeAheadView(routers.APIRootView):
    """
    Typeahead API over de bag, brk, en gebieden datasets
    """


class TypeAheadRouter(routers.DefaultRouter):
    APIRootView = TypeAheadView


class BAGSearchView(routers.APIRootView):
    """
    Full Search API over BAG, BRK en gebieden.
    """


class BAGSearchRouter(routers.DefaultRouter):
    """
    Specifieke functionaliteit voor de Atlas search API.
    """
    APIRootView = BAGSearchView


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
    r'wijk', datasets.bag.views.BuurtcombinatieViewSet)

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

brk.register(
    r'object-expand',
    datasets.brk.views.KadastraalObjectViewSetExpand,
    basename='object-expand',
)

brk.register(r'zakelijk-recht', datasets.brk.views.ZakelijkRechtViewSet)
brk.register(r'aantekening', datasets.brk.views.AantekeningViewSet)

# ##########
# Typeahead
# ###########
typeahead = TypeAheadRouter()

typeahead.register(
    r'bag', views.TypeAheadBagViewSet, basename='typeahead/bag')
typeahead.register(
    r'brk', views.TypeAheadBrkViewSet, basename='typeahead/brk')
typeahead.register(
    r'gebieden', views.TypeAheadGebiedenViewSet,
    basename='typeahead/gebieden')


# ##########
# Typeahead
# ###########
bag_search = BAGSearchRouter()

# Alias voor nummeraanduiding
bag_search.register(
    r'adres',
    views.SearchNummeraanduidingViewSet, basename='search/adres')
bag_search.register(
    r'bouwblok',
    views.SearchBouwblokViewSet, basename='search/bouwblok')
bag_search.register(
    r'gebied',
    views.SearchGebiedenViewSet, basename='search/gebied')
bag_search.register(
    r'kadastraalsubject',
    views.SearchSubjectViewSet, basename='search/kadastraalsubject')

bag_search.register(
    r'postcode',
    views.SearchPostcodeViewSet, basename='search/postcode')

bag_search.register(
    r'kadastraalsubject',
    views.SearchSubjectViewSet, basename='search/kadastraalsubject')
bag_search.register(
    r'kadastraalobject',
    views.SearchObjectViewSet, basename='search/kadastraalobject')
bag_search.register(
    r'openbareruimte',
    views.SearchOpenbareRuimteViewSet, basename='search/openbareruimte')
bag_search.register(
    r'pand',
    views.SearchPandViewSet, basename='search/pand')

