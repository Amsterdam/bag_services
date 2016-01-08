from rest_framework import serializers
from rest_framework.reverse import reverse

from datasets.generic import rest
from . import models


class BrkMixin(rest.DataSetSerializerMixin):
    dataset = 'brk'


# list serializers
class Gemeente(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            '_display',
            'gemeente',
        )


class KadastraleGemeente(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    gemeente = Gemeente()

    class Meta:
        model = models.KadastraleGemeente
        fields = (
            '_links',
            '_display',
            'naam',
            'gemeente',
        )


class KadastraleSectie(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.KadastraleSectie
        fields = (
            '_links',
            '_display',
            'sectie',
        )


class Beschikkingsbevoegdheid(serializers.ModelSerializer):
    class Meta:
        model = models.Beschikkingsbevoegdheid


class Geslacht(serializers.ModelSerializer):
    class Meta:
        model = models.Geslacht


class AanduidingNaam(serializers.ModelSerializer):
    class Meta:
        model = models.AanduidingNaam


class Land(serializers.ModelSerializer):
    class Meta:
        model = models.Land


class Rechtsvorm(serializers.ModelSerializer):
    class Meta:
        model = models.Rechtsvorm


class Adres(serializers.ModelSerializer):
    buitenland_land = Land()

    class Meta:
        model = models.Adres
        fields = (
            'openbareruimte_naam',
            'huisnummer',
            'huisletter',
            'toevoeging',
            'postcode',
            'woonplaats',
            'postbus_nummer',
            'postbus_postcode',
            'postbus_woonplaats',
            'buitenland_adres',
            'buitenland_woonplaats',
            'buitenland_regio',
            'buitenland_naam',
            'buitenland_land',
        )


class KadastraalSubject(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',
            'naam',
        )


class SoortGrootte(serializers.ModelSerializer):
    class Meta:
        model = models.SoortGrootte


class CultuurCodeOnbebouwd(serializers.ModelSerializer):
    class Meta:
        model = models.CultuurCodeOnbebouwd


class CultuurCodeBebouwd(serializers.ModelSerializer):
    class Meta:
        model = models.CultuurCodeBebouwd


class KadastraalObject(BrkMixin, rest.HALSerializer):
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


class AardZakelijkRecht(serializers.ModelSerializer):
    class Meta:
        model = models.AardZakelijkRecht


class AppartementsrechtsSplitsType(serializers.ModelSerializer):
    class Meta:
        model = models.AppartementsrechtsSplitsType


class ZakelijkRecht(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            '_display',
            'id',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context['request']

        data['object_href'] = reverse(
                'kadastraalobject-detail',
                kwargs={'pk': instance.kadastraal_object.id},
                request=request
        )

        user = request.user
        if instance.kadastraal_subject.type == instance.kadastraal_subject.SUBJECT_TYPE_NATUURLIJK \
                and not user.has_perm('brk.view_sensitive_details'):
            data['subject_href'] = reverse('zakelijkrecht-subject', args=(instance.id,), request=request)
        else:
            data['subject_href'] = reverse('kadastraalsubject-detail', kwargs={'pk': instance.kadastraal_subject.id},
                                           request=request)

        return data


class AardAantekening(serializers.ModelSerializer):
    class Meta:
        model = models.AardAantekening


class Aantekening(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    opgelegd_door = KadastraalSubject()

    class Meta:
        model = models.Aantekening
        fields = (
            '_links',
            '_display',
            'id',
            'opgelegd_door',
        )


# detail serializers
class GemeenteDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    gemeente = serializers.CharField()

    class Meta:
        model = models.Gemeente
        fields = (
            '_links',
            '_display',
            'gemeente',
            'geometrie',
        )


class KadastraleGemeenteDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    gemeente = Gemeente()
    secties = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraleGemeente
        fields = (
            '_links',
            '_display',
            'id',
            'gemeente',
            'geometrie',
            'secties',
        )


class KadastraleSectieDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    kadastrale_gemeente = KadastraleGemeente()

    class Meta:
        model = models.KadastraleSectie
        fields = (
            '_links',
            '_display',
            'id',
            'kadastrale_gemeente',
            'sectie',
            'geometrie',
        )


class KadastraalSubjectDetailWithPersonalData(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    woonadres = Adres()
    postadres = Adres()
    beschikkingsbevoegdheid = Beschikkingsbevoegdheid()
    geslacht = Geslacht()
    aanduiding_naam = AanduidingNaam()
    geboorteland = Land()
    land_waarnaar_vertrokken = Land()
    rechtsvorm = Rechtsvorm()

    aantekeningen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',

            'type',
            'beschikkingsbevoegdheid',

            'voornamen',
            'voorvoegsels',
            'naam',
            'geslacht',
            'aanduiding_naam',
            'geboortedatum',
            'geboorteplaats',
            'geboorteland',
            'overlijdensdatum',

            'partner_voornamen',
            'partner_voorvoegsels',
            'partner_naam',

            'land_waarnaar_vertrokken',

            'rsin',
            'kvknummer',
            'rechtsvorm',
            'statutaire_naam',
            'statutaire_zetel',

            'bron',
            'woonadres',
            'postadres',

            'aantekeningen',
        )


class KadastraalSubjectDetail(KadastraalSubjectDetailWithPersonalData):
    rechten = rest.RelatedSummaryField()

    allowed_anonymous = {'_links', '_display', 'id', 'volledige_naam', 'is_natuurlijk_persoon'}

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',

            'id',
            'beschikkingsbevoegdheid',

            'volledige_naam',
            'is_natuurlijk_persoon',

            'voornamen',
            'voorvoegsels',
            'naam',
            'geslacht',
            'aanduiding_naam',
            'geboortedatum',
            'geboorteplaats',
            'geboorteland',
            'overlijdensdatum',

            'partner_voornamen',
            'partner_voorvoegsels',
            'partner_naam',

            'land_waarnaar_vertrokken',

            'rsin',
            'kvknummer',
            'rechtsvorm',
            'statutaire_naam',
            'statutaire_zetel',

            'bron',
            'woonadres',
            'postadres',

            'aantekeningen',
            'rechten',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context['request'].user
        if instance.type == instance.SUBJECT_TYPE_NATUURLIJK and not user.has_perm('brk.view_sensitive_details'):
            return {f: data[f] for f in self.fields.keys() if f in self.allowed_anonymous}

        return data


class KadastraalObjectDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    kadastrale_gemeente = KadastraleGemeente()
    sectie = KadastraleSectie()
    soort_grootte = SoortGrootte()
    cultuurcode_onbebouwd = CultuurCodeOnbebouwd()
    cultuurcode_bebouwd = CultuurCodeBebouwd()

    rechten = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    aantekeningen = rest.RelatedSummaryField()
    a_percelen = rest.RelatedSummaryField()
    g_percelen = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()

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

            'geometrie',

            'g_percelen',
            'a_percelen',
            'verblijfsobjecten',
            'rechten',
            'aantekeningen',
            'beperkingen',
        )


class ZakelijkRechtDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aard_zakelijk_recht = AardZakelijkRecht()
    ontstaan_uit = KadastraalSubject()
    betrokken_bij = KadastraalSubject()
    kadastraal_object = KadastraalObject()
    kadastraal_subject = KadastraalSubject()
    app_rechtsplitstype = AppartementsrechtsSplitsType()

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            '_display',
            'id',
            'aard_zakelijk_recht',
            'aard_zakelijk_recht_akr',

            'ontstaan_uit',
            'betrokken_bij',

            'teller',
            'noemer',

            'kadastraal_object',
            'kadastraal_subject',

            'kadastraal_object_status',

            'app_rechtsplitstype',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context['request']
        user = request.user
        if instance.kadastraal_subject.type == instance.kadastraal_subject.SUBJECT_TYPE_NATUURLIJK \
                and not user.has_perm('brk.view_sensitive_details'):
            data['kadastraal_subject'] = reverse('zakelijkrecht-subject',
                                                 args=(instance.id,),
                                                 request=request)

        return data


class AantekeningDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aard_aantekening = AardAantekening()
    kadastraal_object = KadastraalObject()
    opgelegd_door = KadastraalSubject()

    class Meta:
        model = models.Aantekening
        fields = (
            '_links',
            '_display',
            'id',
            'aard_aantekening',
            'omschrijving',

            'kadastraal_object',
            'opgelegd_door',
        )
