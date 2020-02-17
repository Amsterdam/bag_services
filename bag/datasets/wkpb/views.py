import logging
from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from swiftclient import ClientException

from objectstore import objectstore
from . import models, serializers
from datasets.generic.rest import DatapuntViewSet

from django_filters.rest_framework.filterset import FilterSet
from django_filters.rest_framework import filters

from bag import authorization_levels

log = logging.getLogger(__name__)

class BroncodeView(DatapuntViewSet):
    """
    BroncodeView

    Het orgaan dat de beperking heeft opgelegd.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/bronleverancier/)
    """
    serializer_class = serializers.Broncode
    serializer_detail_class = serializers.BroncodeDetail
    queryset = models.Broncode.objects.all().order_by('code')
    template_name = "wkpb/broncode.html"


class BeperkingFilter(FilterSet):
    """
    Filter beperkingen op verblijfsobject of kadadstrale objecten
    """

    verblijfsobject = filters.CharFilter(method="vbo_filter")
    verblijfsobject__id = filters.CharFilter(method="vbo_filter")
    verblijfsobject__landelijk_id = filters.CharFilter(method="vbo_filter")

    class Meta(object):
        model = models.Beperking

        fields = (
            'verblijfsobject__id',
            'verblijfsobject__landelijk_id',
            'verblijfsobject',
            'kadastrale_objecten__id',
            'beperkingtype',
            'inschrijfnummer',
        )

    def vbo_filter(self, queryset, _filter_name, value):

        if len(value) == 16:
            return queryset.filter(verblijfsobject__landelijk_id=value)
        return queryset.filter(verblijfsobject__id=value)


class BeperkingView(DatapuntViewSet):
    """
    Wkpb

    De Wkpb is de afkorting voor de Wet kenbaarheid publiekrechtelijke
    beperkingen onroerende zaken.

    Sinds 1 juli 2007 verplicht de Wet kenbaarheid publiekrechtelijke
    beperkingen onroerende zaken (Wkpb) burgemeester
    en wethouders (B&W) van de gemeente Amsterdam om alle bij wet genoemde
    beperkingenbesluiten, daarop betrekking
    hebbende beslissingen in administratief beroep of rechterlijke uitspraken
    en vervallenverklaringen, bedoeld in
    art. 7 lid 4 van de Wkpb, op te nemen in een register en een registratie,
    deze te beheren en daaruit informatie te
    verschaffen.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/)
    """
    serializer_class = serializers.Beperking
    serializer_detail_class = serializers.BeperkingDetail
    queryset = models.Beperking.objects.all().order_by('id')
    queryset_detail = (
        models.Beperking.objects
        .prefetch_related(Prefetch(
            'documenten',
            queryset=models.Brondocument.objects.select_related('bron')
        ))
        .select_related('beperkingtype')
    )
    template_name = "wkpb/beperking.html"

    filterset_class = BeperkingFilter


class BrondocumentView(DatapuntViewSet):
    """
    Brondocument

    Het document dat aan de beperking ten grondslag ligt.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/brondocument/)
    """
    serializer_class = serializers.Brondocument
    serializer_detail_class = serializers.BrondocumentDetail

    queryset = models.Brondocument.objects.select_related('beperking__beperkingtype', 'bron').all().order_by('id')
    filterset_fields = ('bron', 'beperking', )

    def get_serializer_class(self):
        if self.action == 'list' or self.action is None:
            if self.request.is_authorized_for(authorization_levels.SCOPE_WKPB_RBDU):
                return serializers.Brondocument

            return serializers.BrondocumentPublic

        elif self.action == 'retrieve':
            if self.request.is_authorized_for(authorization_levels.SCOPE_WKPB_RBDU):
                return serializers.BrondocumentDetail
            return serializers.BrondocumentDetailPublic

    def retrieve(self, request, *args, **kwargs):
        if 'as_pdf' in self.request.query_params:
            if self.request.is_authorized_for(authorization_levels.SCOPE_WKPB_RBDU):
                brondocument = self.get_object()
                path = f'wkpb/brondocumenten/{brondocument.documentnaam}'
                try:
                    pdf = objectstore.download_wkpb_file_data(path)
                except ClientException as exc:
                    log.error(exc)
                    pdf = None
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="' + brondocument.documentnaam + '"'
                    return response
                else:
                    return Response(data=f'{brondocument.documentnaam} not found', status=HTTP_404_NOT_FOUND)
            else:
                return Response(HTTP_401_UNAUTHORIZED)
        else:
            return super().retrieve(request, *args, **kwargs)
