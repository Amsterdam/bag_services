from django.conf.urls import url, include
from rest_framework import routers
from atlas_api import views
import bag.views

class DocumentedRouter(routers.DefaultRouter):
    def get_api_root_view(self):
        view = super().get_api_root_view()
        print(view)
        view.description = "Hello world"
        return view


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