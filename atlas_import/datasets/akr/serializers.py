from rest_framework import serializers

from . import models
from rest_framework.reverse import reverse


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


class KadastraalSubject(serializers.HyperlinkedModelSerializer):
    titel_of_predikaat = Titel()
    woonadres = Adres()
    postadres = Adres()
    soort_niet_natuurlijke_persoon = NietNatuurlijkePersoon()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            'url',
            'subjectnummer',
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
            'a_nummer'
        )


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


class Verblijfsobjecten(serializers.HyperlinkedRelatedField):
    def get_url(self, obj, view_name, request, fmt):
        return reverse(view_name, kwargs={'pk': obj.vbo_id}, request=request, format=fmt)


class KadastraalObject(serializers.HyperlinkedModelSerializer):
    soort_cultuur_onbebouwd = SoortCultuurOnbebouwd()
    bebouwingscode = BebouwingsCode()
    verblijfsobjecten = Verblijfsobjecten(view_name='verblijfsobject-detail', many=True, read_only=True)

    class Meta:
        model = models.KadastraalObject
        fields = (
            'url',
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
        )