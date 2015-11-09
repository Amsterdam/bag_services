from rest_framework import serializers

from datasets.generic import rest
from . import models


class AkrMixin(rest.DataSetSerializerMixin):
    dataset = 'kadaster'


class NietNatuurlijkePersoon(serializers.ModelSerializer):
    class Meta:
        model = models.NietNatuurlijkePersoon


class Titel(serializers.ModelSerializer):
    class Meta:
        model = models.Titel


class Adres(serializers.ModelSerializer):
    class Meta:
        model = models.Adres
        fields = (
            'aanduiding',
            'adresregel_1',
            'adresregel_2',
            'adresregel_3',
            'huisletter',
            'huisnummer',
            'toevoeging',
            'land',
            'beschrijving',
            'postcode',
            'straatnaam',
            'woonplaats',
        )


class SoortRecht(serializers.ModelSerializer):
    class Meta:
        model = models.SoortRecht


class KadastraalSubject(AkrMixin, rest.HALSerializer):
    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            'subjectnummer',
            'volledige_naam',
        )


class KadastraalSubjectDetail(AkrMixin, rest.HALSerializer):
    titel_of_predikaat = Titel()
    woonadres = Adres()
    postadres = Adres()
    soort_niet_natuurlijke_persoon = NietNatuurlijkePersoon()
    rechten = rest.RelatedSummaryField()

    allowed_anonymous = {'_links', 'subjectnummer', 'volledige_naam', 'natuurlijk_persoon'}

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            'subjectnummer',
            'volledige_naam',
            'natuurlijk_persoon',
            'titel_of_predikaat',
            'geslachtsaanduiding',
            'geslachtsnaam',
            'diacritisch',
            'naam_niet_natuurlijke_persoon',
            'soort_subject',
            'soort_niet_natuurlijke_persoon',
            'voorletters',
            'voornamen',
            'voorvoegsel',
            'geboortedatum',
            'geboorteplaats',
            'overleden',
            'overlijdensdatum',
            'zetel',
            'woonadres',
            'postadres',
            'a_nummer',
            'rechten',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context['request'].user
        if instance.natuurlijk_persoon() and not user.has_perm('akr.view_sensitive_details'):
            for f in self.fields.keys() - self.allowed_anonymous:
                del data[f]

        return data


class SoortCultuurOnbebouwd(serializers.ModelSerializer):
    class Meta:
        model = models.SoortCultuurOnbebouwd
        fields = (
            'code',
            'omschrijving',
        )


class BebouwingsCode(serializers.ModelSerializer):
    class Meta:
        model = models.Bebouwingscode
        fields = (
            'code',
            'omschrijving',
        )


class ZakelijkRecht(AkrMixin, rest.HALSerializer):
    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            'identificatie',
        )


class ZakelijkRechtDetail(AkrMixin, rest.HALSerializer):
    soort_recht = SoortRecht()
    kadastraal_object = 'KadastraalObject'
    kadastraal_subject = 'KadastraalSubject'

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            'identificatie',

            'kadastraal_object',
            'kadastraal_subject',
            'transactie',

            'soort_recht',
            'volgnummer',
            'aandeel_medegerechtigden',
            'aandeel_subject',

            'einde_filiatie',
            'sluimerend',
        )


class KadastraalObject(AkrMixin, rest.HALSerializer):
    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            'id',
        )


class KadastraalObjectDetail(AkrMixin, rest.HALSerializer):
    soort_cultuur_onbebouwd = SoortCultuurOnbebouwd()
    bebouwingscode = BebouwingsCode()

    rechten = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            'gemeentecode',
            'sectie',
            'perceelnummer',
            'objectindex_letter',
            'objectindex_nummer',
            'grootte',
            'grootte_geschat',
            'cultuur_tekst',
            'soort_cultuur_onbebouwd',
            'meer_culturen_onbebouwd',
            'bebouwingscode',
            'kaartblad',
            'ruitletter',
            'ruitnummer',
            'verblijfsobjecten',
            'rechten',
            'geometrie',
            'beperkingen'
        )


class SoortStuk(serializers.ModelSerializer):
    class Meta:
        model = models.SoortStuk


class Transactie(AkrMixin, rest.HALSerializer):
    class Meta:
        model = models.Transactie
        fields = (
            '_links',
            'registercode',
        )


class TransactieDetail(AkrMixin, rest.HALSerializer):
    soort_stuk = SoortStuk()
    rechten = rest.RelatedSummaryField()

    class Meta:
        model = models.Transactie
        fields = (
            '_links',
            'registercode',
            'stukdeel_1',
            'stukdeel_2',
            'stukdeel_3',
            'ontvangstdatum',
            'soort_stuk',
            'verlijdensdatum',
            'meer_kadastrale_objecten',
            'koopjaar',
            'koopsom',
            'belastingplichtige',
            'rechten',
        )
