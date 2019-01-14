from rest_framework import routers

import datasets.bag.views
import datasets.brk.views
import datasets.wkpb.views

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


class WkpbView(routers.APIRootView):
    """
    Wkpd

    De [Gemeentelijke beperkingenregistratie op grond van de Wkpb](https://www.amsterdam.nl/stelselpedia/wkpb-index/)
    bevat alle bij wet genoemde beperkingenbesluiten op onroerende
    zaken, die het gemeentebestuur heeft opgelegd.
    """  # noqa


class WkpbRouter(routers.DefaultRouter):
    APIRootView = WkpbView


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
    base_name='object-expand',
)

brk.register(r'zakelijk-recht', datasets.brk.views.ZakelijkRechtViewSet)
brk.register(r'aantekening', datasets.brk.views.AantekeningViewSet)

wkpb = WkpbRouter()
wkpb.register(r'beperking', datasets.wkpb.views.BeperkingView)
wkpb.register(r'brondocument', datasets.wkpb.views.BrondocumentView)
wkpb.register(r'broncode', datasets.wkpb.views.BroncodeView)

# ##########
# Typeahead
# ###########
typeahead = TypeAheadRouter()

##
# Deprecated!! The old all in one typeahead endpoint
# typeahead.register(r'typeahead', views.TypeAheadLegacyViewSet,
#                    base_name='typeahead')

# The new separate endpoints. Look at the typeahead project
# for combined typeahead

typeahead.register(
    r'bag', views.TypeAheadBagViewSet, base_name='typeahead/bag')
typeahead.register(
    r'brk', views.TypeAheadBrkViewSet, base_name='typeahead/brk')
typeahead.register(
    r'gebieden', views.TypeAheadGebiedenViewSet,
    base_name='typeahead/gebieden')


# ##########
# Typeahead
# ###########
bag_search = BAGSearchRouter()

# Alias voor nummeraanduiding
bag_search.register(
    r'adres',
    views.SearchNummeraanduidingViewSet, base_name='search/adres')
bag_search.register(
    r'bouwblok',
    views.SearchBouwblokViewSet, base_name='search/bouwblok')
bag_search.register(
    r'gebied',
    views.SearchGebiedenViewSet, base_name='search/gebied')
bag_search.register(
    r'kadastraalsubject',
    views.SearchSubjectViewSet, base_name='search/kadastraalsubject')

bag_search.register(
    r'postcode',
    views.SearchPostcodeViewSet, base_name='search/postcode')

bag_search.register(
    r'kadastraalsubject',
    views.SearchSubjectViewSet, base_name='search/kadastraalsubject')
bag_search.register(
    r'kadastraalobject',
    views.SearchObjectViewSet, base_name='search/kadastraalobject')
bag_search.register(
    r'openbareruimte',
    views.SearchOpenbareRuimteViewSet, base_name='search/openbareruimte')
bag_search.register(
    r'landelijk_id',
    views.SearchLandelijkIdViewSet, base_name='search/landelijk_id')

