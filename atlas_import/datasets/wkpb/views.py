from django.db.models import Prefetch

from . import models, serializers
from datasets.generic.rest import AtlasViewSet


class BroncodeView(AtlasViewSet):
    """
    Het orgaan dat de beperking heeft opgelegd.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/bronleverancier/)
    """
    serializer_class = serializers.Broncode
    serializer_detail_class = serializers.BroncodeDetail
    queryset = models.Broncode.objects.all()
    template_name = "wkpb/broncode.html"


class BeperkingView(AtlasViewSet):
    """
    De Wkpb is de afkorting voor de Wet kenbaarheid publiekrechtelijke beperkingen onroerende zaken.

    Sinds 1 juli 2007 verplicht de Wet kenbaarheid publiekrechtelijke beperkingen onroerende zaken (Wkpb) burgemeester
    en wethouders (B&W) van de gemeente Amsterdam om alle bij wet genoemde beperkingenbesluiten, daarop betrekking
    hebbende beslissingen in administratief beroep of rechterlijke uitspraken en vervallenverklaringen, bedoeld in
    art. 7 lid 4 van de Wkpb, op te nemen in een register en een registratie, deze te beheren en daaruit informatie te
    verschaffen.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/)
    """
    serializer_class = serializers.Beperking
    serializer_detail_class = serializers.BeperkingDetail
    queryset = models.Beperking.objects.all()
    queryset_detail = (
        models.Beperking.objects
        .prefetch_related(Prefetch(
            'documenten',
            queryset=models.Brondocument.objects.select_related('bron')
        ))
        .select_related('beperkingtype')
    )
    template_name = "wkpb/beperking.html"
    filter_fields = ('kadastrale_objecten__id', 'verblijfsobjecten__id')


class BrondocumentView(AtlasViewSet):
    """
    Het document dat aan de beperking ten grondslag ligt.

    [Stelselpedia](https://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/brondocument/)
    """
    serializer_class = serializers.Brondocument
    serializer_detail_class = serializers.BrondocumentDetail
    queryset = models.Brondocument.objects.all()
    filter_fields = ('bron', 'beperking', )
