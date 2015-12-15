from rest_framework import serializers

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

    class Meta:
        model = models.KadastraleGemeente
        fields = (
            '_links',
            '_display',
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


class VertrekLand(serializers.ModelSerializer):
    class Meta:
        model = models.VertrekLand


class Rechtsvorm(serializers.ModelSerializer):
    class Meta:
        model = models.Rechtsvorm


class Adres(serializers.ModelSerializer):
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


class AardAantekening(serializers.ModelSerializer):
    class Meta:
        model = models.AardAantekening


class Aantekening(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Aantekening
        fields = (
            '_links',
            '_display',
            'id',
        )


class AardStukdeel(serializers.ModelSerializer):
    class Meta:
        model = models.AardStukdeel


class RegisterCode(serializers.ModelSerializer):
    class Meta:
        model = models.RegisterCode


class SoortRegister(serializers.ModelSerializer):
    class Meta:
        model = models.SoortRegister


class Stukdeel(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

    class Meta:
        model = models.Stukdeel
        fields = (
            '_links',
            '_display',
            'id',
        )


# detail serializers
class GemeenteDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()

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

    class Meta:
        model = models.KadastraleGemeente
        fields = (
            '_links',
            '_display',
            'gemeente',
            'geometrie',
        )


class KadastraleSectieDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    kadastrale_gemeente = KadastraleGemeente()

    class Meta:
        model = models.KadastraleSectie
        fields = (
            '_links',
            '_display',
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
    land_waarnaar_vertrokken = VertrekLand()
    rechtsvorm = Rechtsvorm()

    aantekeningen = rest.RelatedSummaryField()

    allowed_anonymous = {'_links', '_display', 'subjectnummer', 'volledige_naam', 'natuurlijk_persoon'}

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',

            'type',
            'beschikkingsbevoegdheid',
            'bsn',

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
    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context['request'].user
        if instance.type == instance.SUBJECT_TYPE_NATUURLIJK and not user.has_perm('akr.view_sensitive_details'):
            data = [data[f] for f in self.fields.keys() if f in self.allowed_anonymous]

        return data


class KadastraalObjectDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    gemeente = Gemeente()
    kadastrale_gemeente = KadastraleGemeente()
    sectie = KadastraleSectie()
    soort_grootte = SoortGrootte()
    g_perceel = KadastraalObject()
    cultuurcode_onbebouwd = CultuurCodeOnbebouwd()
    cultuurcode_bebouwd = CultuurCodeBebouwd()
    voornaamste_gerechtigde = KadastraalSubject()

    rechten = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    aantekeningen = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'gemeente',
            'kadastrale_gemeente',
            'perceelnummer',
            'index_letter',
            'index_nummer',
            'soort_grootte',
            'grootte',
            'g_perceel',
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
            'voornaamste_gerechtigde',

            'verblijfsobjecten',
            'rechten',
            'aantekeningen',
        )


class ZakelijkRechtDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aard_zakelijk_recht = AardZakelijkRecht()
    ontstaan_uit = ZakelijkRecht()
    betrokken_bij = ZakelijkRecht()
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

            'belast_azt',
            'belast_met_azt',
            'ontstaan_uit',
            'betrokken_bij',

            'beperkt_tot_tng',

            'kadastraal_object',
            'kadastraal_subject',

            'kadastraal_object_status',

            'app_rechtsplitstype',
        )


class AantekeningDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aard_aantekening = AardAantekening()
    kadastraal_object = KadastraalObject()
    zekerheidsrecht = ZakelijkRecht()
    kadastraal_subject = KadastraalSubject()

    class Meta:
        model = models.Aantekening
        fields = (
            '_links',
            '_display',
            'id',
            'aard_aantekening',
            'omschrijving',
            'type',

            'kadastraal_object',
            'zekerheidsrecht',
            'kadastraal_subject',
        )


class StukdeelDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aard_stukdeel = AardStukdeel()
    register_code = RegisterCode()
    soort_register = SoortRegister()
    tenaamstelling = ZakelijkRecht()
    aantekening = Aantekening()

    class Meta:
        model = models.Stukdeel
        fields = (
            '_links',
            '_display',
            'id',
            'aard_stukdeel',
            'koopsom',
            'koopsom_valuta',

            'stuk_id',
            'portefeuille_nummer',
            'tijdstip_aanbieding',
            'reeks_code',
            'volgnummer',
            'register_code',
            'soort_register',

            'deel_soort',

            'tenaamstelling',
            'aantekening',
        )
