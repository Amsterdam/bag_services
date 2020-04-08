from bag import authorization_levels

from rest_framework import serializers
from rest_framework.reverse import reverse

from datasets.wkpb import serializers as wkpb_serializers

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
        fields = '__all__'


class Geslacht(serializers.ModelSerializer):
    class Meta:
        model = models.Geslacht
        fields = '__all__'


class AanduidingNaam(serializers.ModelSerializer):
    class Meta:
        model = models.AanduidingNaam
        fields = '__all__'


class Land(serializers.ModelSerializer):
    class Meta:
        model = models.Land
        fields = '__all__'


class Rechtsvorm(serializers.ModelSerializer):
    class Meta:
        model = models.Rechtsvorm
        fields = '__all__'


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
        fields = '__all__'


class CultuurCodeOnbebouwd(serializers.ModelSerializer):
    class Meta:
        model = models.CultuurCodeOnbebouwd
        fields = '__all__'


class CultuurCodeBebouwd(serializers.ModelSerializer):
    class Meta:
        model = models.CultuurCodeBebouwd
        fields = '__all__'


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
        fields = '__all__'


class AppartementsrechtsSplitsType(serializers.ModelSerializer):
    class Meta:
        model = models.AppartementsrechtsSplitsType
        fields = '__all__'


class ZakelijkRechtContextMixin:

    def get_contextual_subject_href(self, instance, request):
        subject_natuurlijk = \
            instance.kadastraal_subject.type ==  \
            instance.kadastraal_subject.SUBJECT_TYPE_NATUURLIJK

        authorized = request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN)

        if subject_natuurlijk and not authorized:
            return reverse(
                'zakelijkrecht-subject',
                args=(instance.id,), request=request)

        return reverse(
            'kadastraalsubject-detail',
            kwargs={'pk': instance.kadastraal_subject.id},
            request=request
        )


class ZakelijkRecht(BrkMixin, rest.HALSerializer, ZakelijkRechtContextMixin):
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
        data['subject_href'] = \
            self.get_contextual_subject_href(instance, request)

        if 'kadastraal_subject' in request.query_params:
            data['_display'] = instance.directional_name(direction='object')
        else:
            data['_display'] = instance.directional_name(direction='subject')

        data['object_href'] = reverse(
            'kadastraalobject-detail',
            kwargs={'pk': instance.kadastraal_object_id},
            request=self.context['request']
        )

        return data


class AardAantekening(serializers.ModelSerializer):
    class Meta:
        model = models.AardAantekening
        fields = '__all__'


class Aantekening(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    opgelegd_door = KadastraalSubject()

    class Meta:
        model = models.Aantekening
        fields = (
            '_links',
            '_display',
            'id',
            'aantekening_id',
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

            'id',
            'type',
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
        )


class ZakelijkRechtDetail(
        BrkMixin, rest.HALSerializer, ZakelijkRechtContextMixin):
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


class ZakelijkRechtDetailPublic(
        BrkMixin, rest.HALSerializer, ZakelijkRechtContextMixin):
    _display = rest.DisplayField()
    aard_zakelijk_recht = AardZakelijkRecht()
    # ontstaan_uit = KadastraalSubject()
    # betrokken_bij = KadastraalSubject()
    kadastraal_object = KadastraalObject()
    # kadastraal_subject = KadastraalSubject()
    app_rechtsplitstype = AppartementsrechtsSplitsType()

    class Meta:
        model = models.ZakelijkRecht
        fields = (
            '_links',
            '_display',
            'id',
            'aard_zakelijk_recht',
            'aard_zakelijk_recht_akr',

            # 'ontstaan_uit',
            # 'betrokken_bij',

            'teller',
            'noemer',

            'kadastraal_object',
            # 'kadastraal_subject',

            'kadastraal_object_status',

            'app_rechtsplitstype',
        )


class KadastraalSubjectDetail(KadastraalSubjectDetailWithPersonalData):
    rechten = rest.RelatedSummaryField()

    class Meta:
        model = models.KadastraalSubject
        fields = (
            '_links',
            '_display',

            'id',
            'type',
            'beschikkingsbevoegdheid',

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
            'rechten',        # employee NOT OK for natuurlijk
        )

    def to_representation(self, subject):
        """
        Remove 'rechten' if not plus user
        """
        data = super().to_representation(subject)

        if subject.type == subject.SUBJECT_TYPE_NIET_NATUURLIJK:
            return data

        # check if we are authorized voor natuurlijke personen
        request = self.context['request']
        if request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN):
            return data

        # We are employee and should not see 'rechten' / eigendommen
        data.pop('rechten')

        return data


class KadastraalObjectDetail(BrkMixin, rest.HALSerializer):
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    objectnummer = serializers.CharField(source='perceelnummer')
    kadastrale_gemeente = KadastraleGemeente()
    sectie = KadastraleSectie()
    soort_grootte = SoortGrootte()
    cultuurcode_onbebouwd = CultuurCodeOnbebouwd()
    cultuurcode_bebouwd = CultuurCodeBebouwd()

    rechten = rest.RelatedSummaryField()
    verblijfsobjecten = rest.RelatedSummaryField()
    _adressen = rest.AdresFilterField()
    aantekeningen = rest.RelatedSummaryField()

    # a_percelen = rest.RelatedSummaryField(source='a_percelen')
    betrokken_bij = rest.RelatedSummaryField(source='a_percelen')

    # g_percelen = rest.RelatedSummaryField(source='g_percelen')
    ontstaan_uit = rest.RelatedSummaryField(source='g_percelen')

    beperkingen = rest.RelatedSummaryField()
    geometrie = rest.MultipleGeometryField()

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'kadastrale_gemeente',
            'sectie',
            'objectnummer',
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

            'geometrie',

            'ontstaan_uit',
            'betrokken_bij',

            'verblijfsobjecten',
            '_adressen',
            'rechten',
            'aantekeningen',
            'beperkingen',
        )


class KadastraalObjectDetailPublic(BrkMixin, rest.HALSerializer):
    """
    Public version kadastraal object

    Forbidden fields:

    koopsom, koopjaar, cultuur (on)bebouwd, rechten en aantekeningen

    https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:aa:datarestricties&s[]=restricties # noqa
    """
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    objectnummer = serializers.CharField(source='perceelnummer')
    kadastrale_gemeente = KadastraleGemeente()
    sectie = KadastraleSectie()
    soort_grootte = SoortGrootte()

    verblijfsobjecten = rest.RelatedSummaryField()
    _adressen = rest.AdresFilterField()

    # a_percelen = rest.RelatedSummaryField(source='a_percelen')
    betrokken_bij = rest.RelatedSummaryField(source='a_percelen')

    # g_percelen = rest.RelatedSummaryField(source='g_percelen')
    ontstaan_uit = rest.RelatedSummaryField(source='g_percelen')

    beperkingen = rest.RelatedSummaryField()
    geometrie = rest.MultipleGeometryField()

    grootte = rest.DecimalSpecial(max_digits=10, decimal_places=2)

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'kadastrale_gemeente',
            'sectie',
            'objectnummer',
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

            'geometrie',

            'ontstaan_uit',
            'betrokken_bij',

            'verblijfsobjecten',
            '_adressen',
            'beperkingen',
        )


class KadastraalObjectDetailExpand(KadastraalObjectDetail):
    rechten = ZakelijkRechtDetail(many=True)
    aantekeningen = Aantekening(many=True)

    ontstaan_uit = KadastraalObject(source='g_percelen', many=True)
    betrokken_bij = KadastraalObject(source='a_percelen', many=True)

    beperkingen = wkpb_serializers.BeperkingDetail(many=True)


class KadastraalObjectDetailExpandPublic(KadastraalObjectDetailPublic):

    ontstaan_uit = KadastraalObject(source='g_percelen', many=True)
    betrokken_bij = KadastraalObject(source='a_percelen', many=True)

    beperkingen = wkpb_serializers.BeperkingDetail(many=True)


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


class KadastraalObjectNummeraanduiding(BrkMixin, rest.HALSerializer):
    """
    Serializer used in custom nummeraanduiding endpoint
    """
    _display = rest.DisplayField()
    aanduiding = serializers.CharField(source='get_aanduiding_spaties')
    rechten = rest.RelatedSummaryField()
    beperkingen = rest.RelatedSummaryField()
    aantekeningen = rest.RelatedSummaryField()
    a_percelen = KadastraalObject(many=True)
    g_percelen = KadastraalObject(many=True)

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'rechten',
            'beperkingen',
            'aantekeningen',
            'a_percelen',
            'g_percelen',
        )


class KadastraalObjectNummeraanduidingExp(KadastraalObjectNummeraanduiding):
    rechten = ZakelijkRechtDetail(many=True)
    beperkingen = wkpb_serializers.BeperkingDetail(many=True)
    aantekeningen = Aantekening(many=True)

    class Meta:
        model = models.KadastraalObject
        fields = (
            '_links',
            '_display',
            'id',
            'aanduiding',
            'rechten',
            'beperkingen',
            'aantekeningen',
        )
