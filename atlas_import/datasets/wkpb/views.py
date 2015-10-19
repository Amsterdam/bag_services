from . import models, serializers
from datasets.generic.rest import AtlasViewSet


class BeperkingKadastraalObjectView(AtlasViewSet):
    """
    De Wkpb is de afkorting voor de Wet kenbaarheid publiekrechtelijke beperkingen onroerende zaken.

    Sinds 1 juli 2007 verplicht de Wet kenbaarheid publiekrechtelijke beperkingen onroerende zaken (Wkpb) burgemeester
    en wethouders (B&W) van de gemeente Amsterdam om alle bij wet genoemde beperkingenbesluiten, daarop betrekking
    hebbende beslissingen in administratief beroep of rechterlijke uitspraken en vervallenverklaringen, bedoeld in
    art. 7 lid 4 van de Wkpb, op te nemen in een register en een registratie, deze te beheren en daaruit informatie te
    verschaffen.
    """
    serializer_class = serializers.BeperkingKadastraalObject
    queryset = models.BeperkingKadastraalObject.objects.all()


class BeperkingView(AtlasViewSet):
    """
    Lijst van beperkingen op een gebruiksrecht.
    """
    serializer_class = serializers.Beperking
    queryset = models.Beperking.objects.all()
