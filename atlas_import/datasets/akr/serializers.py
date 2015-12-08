from rest_framework import serializers
from rest_framework.reverse import reverse

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
    _display = rest.DisplayField()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',
            'subjectnummer',
            'volledige_naam',
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


class ZakelijkRecht(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            '_display',
            'identificatie',
        )


class KadastraalObject(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding'
        )


class SoortStuk(serializers.ModelSerializer):
    class Meta:
        model = models.SoortStuk


class Transactie(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Transactie
        fields = (
            '_links',
            '_display',
            'registercode',
            'koopjaar',
            'koopsom',
            'meer_kadastrale_objecten',
        )


class ZakelijkRechtDetail(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    soort_recht = SoortRecht()
    kadastraal_object = KadastraalObject()
    kadastraal_subject = KadastraalSubject()
    transactie = Transactie()

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            '_display',
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

            'begin_geldigheid',
            'einde_geldigheid',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context['request']
        user = request.user
        if instance.kadastraal_subject.natuurlijk_persoon() and not user.has_perm('akr.view_sensitive_details'):
            data['kadastraal_subject'] = reverse('zakelijkrecht-subject',
                                                 args=(instance.id,),
                                                 request=request)

        return data


class KadastraalSubjectDetail(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    titel_of_predikaat = Titel()
    woonadres = Adres()
    postadres = Adres()
    soort_niet_natuurlijke_persoon = NietNatuurlijkePersoon()
    rechten = rest.RelatedSummaryField()

    allowed_anonymous = {'_links', '_display', 'subjectnummer', 'volledige_naam', 'natuurlijk_persoon'}

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',
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


class KadastraalSubjectDetailWithPersonalData(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    titel_of_predikaat = Titel()
    woonadres = Adres()
    postadres = Adres()
    soort_niet_natuurlijke_persoon = NietNatuurlijkePersoon()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',
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
        )


class KadastraalObjectDetail(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    soort_cultuur_onbebouwd = SoortCultuurOnbebouwd()
    bebouwingscode = BebouwingsCode()

    rechten = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
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
            'beperkingen',
            'omschrijving_deelperceel',
        )


class TransactieDetail(AkrMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    soort_stuk = SoortStuk()
    rechten = rest.RelatedSummaryField()

    class Meta:
        model = models.Transactie
        fields = (
            '_links',
            '_display',
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
