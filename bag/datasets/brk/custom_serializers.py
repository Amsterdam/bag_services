from rest_framework import serializers

from datasets.generic import rest
from datasets.brk import models
from datasets.brk import serializers as brk_serializers
from datasets.bag.serializers import Verblijfsobject
from datasets.wkpb.serializers import BeperkingDetail


class KadastraalObjectDetailWkpb(brk_serializers.BrkMixin, rest.HALSerializer):
    """
    Serializer used in custom wkpb endpoint
    """
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    kadastrale_gemeente = brk_serializers.KadastraleGemeente()
    sectie = brk_serializers.KadastraleSectie()
    soort_grootte = brk_serializers.SoortGrootte()
    cultuurcode_onbebouwd = brk_serializers.CultuurCodeOnbebouwd()
    cultuurcode_bebouwd = brk_serializers.CultuurCodeBebouwd()

    rechten = brk_serializers.ZakelijkRecht(many=True)
    verblijfsobjecten = Verblijfsobject(many=True)
    beperkingen = BeperkingDetail(many=True)
    aantekeningen = rest.RelatedSummaryField()
    a_percelen = rest.RelatedSummaryField()
    g_percelen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'kadastrale_gemeente',
            'sectie',
            'perceelnummer',
            'indexletter',
            'indexnummer',
            'soort_grootte',
            'grootte',
            'koopsom',
            'koopsom_valuta_code',
            'koopjaar',
            'meer_objecten',
            'cultuurcode_onbebouwd',
            'cultuurcode_bebouwd',

            'register9_tekst',
            'status_code',
            'toestandsdatum',
            'voorlopige_kadastrale_grens',
            'in_onderzoek',

            'g_percelen',
            'a_percelen',
            'verblijfsobjecten',
            'rechten',
            'aantekeningen',
            'beperkingen',
        )


class KadastraalObjectDetailWkpbPublic(KadastraalObjectDetailWkpb):
    """
    Serializer used in custom wkpb endpoint
    """
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    kadastrale_gemeente = brk_serializers.KadastraleGemeente()
    sectie = brk_serializers.KadastraleSectie()
    soort_grootte = brk_serializers.SoortGrootte()
    verblijfsobjecten = Verblijfsobject(many=True)
    beperkingen = BeperkingDetail(many=True)
    aantekeningen = rest.RelatedSummaryField()
    a_percelen = rest.RelatedSummaryField()
    g_percelen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'kadastrale_gemeente',
            'sectie',
            'perceelnummer',
            'indexletter',
            'indexnummer',
            'soort_grootte',
            'grootte',
            'meer_objecten',

            'register9_tekst',
            'status_code',
            'toestandsdatum',
            'voorlopige_kadastrale_grens',
            'in_onderzoek',

            'g_percelen',
            'a_percelen',
            'verblijfsobjecten',
            'beperkingen',
        )
