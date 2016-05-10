from rest_framework import serializers

from datasets.generic import rest
from datasets.brk import models
from datasets.brk import serializers as brk_serializers


class KadastraalObjectNummeraanduiding(brk_serializers.BrkMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    rechten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()
    a_percelen = rest.RelatedSummaryField()
    g_percelen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'rechten',
            'beperkingen',
            'a_percelen',
            'g_percelen',
        )


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
    verblijfsobjecten = brk_serializers.Verblijfsobject(many=True)
    beperkingen = brk_serializers.BeperkingDetail(many=True)
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
            'index_letter',
            'index_nummer',
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
