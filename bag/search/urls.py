# from rest_framework import routers
#
# from search import views
#
#
# class SearchView(routers.APIRootView):
#     """
#     Search
#
#     End point for different search uris, offering data not directly reflected
#     in the models
#     """
#
#
# class SearchRouter(routers.DefaultRouter):
#     APIRootView = SearchView
#
#
# class TypeAheadView(routers.APIRootView):
#     """
#     Typeahead API over de bag, brk, en gebieden datasets
#     """
#
#
# class TypeAheadRouter(routers.DefaultRouter):
#     APIRootView = TypeAheadView
#
#
# class BAGSearchView(routers.APIRootView):
#     """
#     Full Search API over BAG, BRK en gebieden.
#     """
#
#
# class BAGSearchRouter(routers.DefaultRouter):
#     """
#     Specifieke functionaliteit voor de Atlas search API.
#     """
#     APIRootView = BAGSearchView

# # ##########
# # Typeahead
# # ###########
# typeahead = TypeAheadRouter()

# #
# Deprecated!! The old all in one typeahead endpoint
# typeahead.register(r'typeahead', views.TypeAheadLegacyViewSet,
#                    base_name='typeahead')
#
# The new separate endpoints. Look at the typeahead project
# for combined typeahead

# # ##########
# # Typeahead
# # ###########
# bag_search = BAGSearchRouter()
#
# # Alias voor nummeraanduiding
# bag_search.register(
#     r'adres',
#     views.SearchNummeraanduidingViewSet, base_name='search/adres')
# bag_search.register(
#     r'bouwblok',
#     views.SearchBouwblokViewSet, base_name='search/bouwblok')
# bag_search.register(
#     r'gebied',
#     views.SearchGebiedenViewSet, base_name='search/gebied')
# bag_search.register(
#     r'kadastraalsubject',
#     views.SearchSubjectViewSet, base_name='search/kadastraalsubject')
#
# bag_search.register(
#     r'postcode',
#     views.SearchPostcodeViewSet, base_name='search/postcode')
#
# bag_search.register(
#     r'kadastraalsubject',
#     views.SearchSubjectViewSet, base_name='search/kadastraalsubject')
# bag_search.register(
#     r'kadastraalobject',
#     views.SearchObjectViewSet, base_name='search/kadastraalobject')
# bag_search.register(
#     r'openbareruimte',
#     views.SearchOpenbareRuimteViewSet, base_name='search/openbareruimte')
# bag_search.register(
#     r'pand',
#     views.SearchPandViewSet, base_name='search/pand')
#
