from django.shortcuts import get_object_or_404

from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from rest_framework import serializers as drf_serializers
from rest_framework.status import HTTP_401_UNAUTHORIZED

from datasets.brk import models, serializers, custom_serializers
from datasets.generic.rest import DatapuntViewSet
from datasets.generic import rest

from django_filters.rest_framework import filters
from django_filters.rest_framework import FilterSet

from bag import authorization_levels

import logging

log = logging.getLogger(__name__)


class GemeenteViewSet(DatapuntViewSet):
    """
    Gemeente.

    Een gemeente is een afgebakend gedeelte van het grondgebied van Nederland,
    ingesteld op basis van artikel 123 van
    de Grondwet.

    Verder is een gemeente zelfstandig, heeft zij zelfbestuur en is onderdeel
    van de staat. Zij staat onder bestuur van
    een raad, een burgemeester en wethouders.

    De gemeentegrens wordt door de centrale overheid vastgesteld, en door het
    Kadaster vastgelegd.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/brk-index/catalogus/objectklasse-2/)

    ---

    """
    queryset = models.Gemeente.objects.all().order_by('gemeente')
    serializer_class = serializers.Gemeente
    serializer_detail_class = serializers.GemeenteDetail
    lookup_value_regex = '[^/]+'


class KadastraleGemeenteViewSet(DatapuntViewSet):
    """
    Kadastrale gemeente

    De kadastrale gemeente is het eerste gedeelte van de aanduiding van een
    kadastraal perceel.

    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    queryset = (models.KadastraleGemeente.objects
                .select_related('gemeente')
                .all().order_by('id'))
    serializer_class = serializers.KadastraleGemeente
    serializer_detail_class = serializers.KadastraleGemeenteDetail
    lookup_value_regex = '[^/]+'


class KadastraleSectieViewSet(DatapuntViewSet):
    """
    Kadastrale sectie

    Een sectie is een onderdeel van een kadastrale gemeente en als
    zodanig een onderdeel van de kadastrale aanduiding waarbinnen
    uniek genummerde percelen zijn gelegen.

    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    queryset = models.KadastraleSectie.objects.all().order_by('id')
    queryset_detail = (
        models.KadastraleSectie.objects.select_related(
            'kadastrale_gemeente', 'kadastrale_gemeente__gemeente'))
    serializer_class = serializers.KadastraleSectie
    serializer_detail_class = serializers.KadastraleSectieDetail
    filter_fields = ('kadastrale_gemeente',)


class SubjectFilter(FilterSet):
    """
    Filter subjecten.
    """
    buurt = filters.CharFilter(method="buurt_filter", label='buurt')

    zakelijk_recht = filters.NumberFilter(
        method="recht_filter", label='recht')

    bewoners = filters.BooleanFilter(method="bewoners_filter")

    class Meta(object):
        model = models.KadastraalSubject

        fields = (
            'naam',
            'type',
            'buurt',
            'kvknummer',
            'statutaire_naam',
            'zakelijk_recht',
        )

    def buurt_filter(self, queryset, _filter_name, value):
        """
        Buurt code 4 chars
        """
        recht_type = 2  # eigenaar

        if 'zakelijk_recht' in self.request.GET:
            recht_type = self.request.GET['zakelijk_recht']

        if len(value) != 4:
            raise drf_serializers.ValidationError('Buurt vollcode is 4 chars')

        # remove ordering.
        # SUPER SLOW because of some weirdness.
        qs = queryset.order_by()

        return qs.filter(
            rechten__verblijfsobjecten__buurt__vollcode=value,
            rechten__aard_zakelijk_recht__code=recht_type
        )

    def recht_filter(self, queryset, _filter_name, value):

        if self.request.GET['buurt']:
            # will be recht filter will be done
            # in buurt filter
            return queryset

        return queryset.filter(
            rechten__aard_zakelijk_recht__code=value
        )


class KadastraalSubjectViewSet(DatapuntViewSet):
    """
    Kadastraal subject

    Een subject is een persoon die in de kadastrale vastgoedregistratie
    voorkomt.

    Het betreft hier zowel natuurlijke als niet natuurlijke personen die
    verschillende rollen kunnen hebben in de kadastrale vastgoedregistratie.

    Dezelfde personen kunnen als verschillende subjecten (met verschillende
    subjectnummers) bekend zijn bij (de verschillende vestigingen van)
    het Kadaster.

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/objectklasse-0/)

    Authorisatie:

    public   - none
    employee - alleen niet natuurlijk
    plus     - mag alles zien
    """
    queryset = models.KadastraalSubject.objects.all().order_by('id')

    queryset_detail = (
        models.KadastraalSubject.objects.select_related(
            'rechtsvorm', 'woonadres', 'woonadres__buitenland_land',
            'postadres', 'postadres__buitenland_land'))

    serializer_class = serializers.KadastraalSubject
    serializer_detail_class = serializers.KadastraalSubjectDetail
    lookup_value_regex = '[^/]+'

    filter_class = SubjectFilter

    # NOTE in serializer there is MORE authorization code!!

    def list(self, request, *args, **kwargs):
        if request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return super().list(request, *args, **kwargs)
        return Response(status=HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        if request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return super().retrieve(request, *args, **kwargs)

        return Response(status=HTTP_401_UNAUTHORIZED)


class KadastraalObjectFilter(FilterSet):
    """
    Filter also capable of dealing with landelijk_ids
    """

    verblijfsobject = filters.CharFilter(method="vbo_filter")
    verblijfsobjecten__id = filters.CharFilter(method="vbo_filter")
    verblijfsobjecten__landelijk_id = filters.CharFilter(method="vbo_filter")

    class Meta(object):
        model = models.KadastraalObject

        fields = (
            'verblijfsobject',
            'verblijfsobjecten__id',
            'verblijfsobjecten__landelijk_id',
            'beperkingen__id',
            'a_percelen__id',
            'g_percelen__id')

    def vbo_filter(self, queryset, _filter_name, value):

        if len(value) == 16:
            return queryset.filter(verblijfsobjecten__landelijk_id=value)

        return queryset.filter(verblijfsobjecten__id=value)


class KadastraalObjectViewSet(DatapuntViewSet):
    """
    Kadastraal object

    Een kadastraal object een onroerende zaak of een appartementsrecht
    waarvoor bij overdracht of vestiging van rechten
    inschrijving in de [openbare
    registers]
    (http://wetten.overheid.nl/BWBR0005291/Boek3/Titel1/Afdeling2/Artikel16/)
    van het Kadaster is vereist.

    Een onroerende zaak heeft een kadastrale aanduiding geheel perceel of
    gedeeltelijk (deel-)perceel.

    Op dit moment komen er nog deelpercelen voor, deze worden uitgefaseerd en
    vervangen door
    "voorlopige perceelgeometrie". De typen perceel, deelperceel en
    appartementsrecht zijn als volgt gedefinieerd.

    # Perceel
    Een perceel is een onroerende zaak, kadastraal geïdentificeerd en met
    kadastrale grenzen begrensd deel van het
    Nederlands grondgebied.
    (definitie is ontleend aan

    [art. 1 Kadasterwet]
    (http://wetten.overheid.nl/zoeken_op/BWBR0004541/Hoofdstuk1/Artikel1/)).

    Als onderdeel van het Nederlands grondgebied is het een driedimensionaal
    ruimtelijk object.

    # Deelperceel
    Een nog niet uitgemeten deel van een kadastraal perceel, bijvoorbeeld een
    stuk van een geheel perceel dat verkocht
    is, of overgaat in een nieuw te vormen perceel. De grenzen van de nieuw te
    vormen percelen (het verkochte en het
    resterende deel) moeten nog worden aangewezen, ingemeten en opgenomen in
    de Kadastrale Kaart. Dat gebeurt
    doorgaans na de inschrijving in de openbare registers. Als de deelpercelen
    ingemeten zijn, gaan deze op in een
    nieuw geheel perceel met een nieuwe kadastrale aanduiding, en is na te
    gaan waar dit kadastraal object ligt.

    # Appartementsrecht
    Een appartementsrecht (art. 5:106 Burgerlijk Wetboek) is geen zaak (art.
    3:2 Burgerlijk Wetboek),
    maar een zakelijk recht dat kadastraal is aangeduid, bestaande uit een
    aandeel in recht(en) op een onroerende
    zaak die in de splitsing is betrokken en dat de bevoegdheid omvat tot het
    uitsluitend gebruik van bepaalde
    gedeelten van deze onroerende zaak,
    die blijkens hun inrichting bestemd zijn of worden om als afzonderlijk
    geheel te worden gebruikt.

    Het aandeel omvat de bevoegdheid tot het uitsluitend gebruik van bepaalde
    gedeelten van een of meer gebouwen en/of
    van de bij het gebouw behorende grond.

    # Appartementencomplex
    Een complex is een object dat beoogt ten behoeve van splitsing in
    appartementsrechten, de in de splitsing
    betrokken kadastrale percelen (de zogenaamde grondpercelen) administratief
    samen te voegen. Van een complex worden verder geen gegevens vastgelegd.

    De kadastrale aanduiding van een complex is een kadastrale aanduiding
    waarvan de index bestaat uit de indexletter
    A en het indexnummer 0000.

    Voordat de rechten van één of meer percelen gesplitst worden in
    appartementsrechten vindt de complexvorming plaats,
    waarbij tevens de kadastrale aanduidingen van de appartementsrechten
    worden aangebracht.
    Naast de onderlinge relaties worden tevens de relaties gelegd van
    het complex naar de betreffende kadastrale percelen waarvan de rechten
    in de splitsing worden betrokken.

    # Voorlopige Kadastrale grenzen
    Wanneer een gedeelte van een perceel wordt verkocht, of een perceel wordt
    gesplitst, verandert de ligging van de kadastrale grens.

    Voorheen was het gebruikelijk na de inschrijving van de akte van koop en
    verkoop de nieuwe grenzen te laten inmeten door het Kadaster.

    Op dit moment kunnen professionele rechthebbenden of een notaris altijd
    voorafgaand aan de inschrijving van een transportakte de kadastrale
    perceelsvorming laten plaatsvinden.

    De voorlopige perceelsgrenzen worden ingetekend m.b.v. de door het
    Kadaster beschikbaar gestelde applicatie ‘SPLITS’.

    Na de inschrijving van de akte vindt de aanwijzing plaats door
    belanghebbenden, en meet de landmeter de definitieve ligging van de
    perceelsgrenzen in.

    Een uitgebreide beschrijving van de aanleiding en het proces is na te
    lezen in het artikel in het vakblad
    [Geo-info (PDF, 359 kB)]
    (http://www.amsterdam.nl/publish/pages/559654/12_kadaster_voorlopige_kadastrale_grenzen.pdf).

    ## Herkenbaarheid in LKI en Massale Output

    In de leveringen van LKI
    ([Kadastrale Kaart](http://www.amsterdam.nl/stelselpedia/woordenboek/))
    ([art. 48 lid 3 Kadasterwet]
    (http://wetten.overheid.nl/BWBR0004541/Hoofdstuk3/Titel1/Artikel48/))
    zijn voorlopige kadastrale grenzen herkenbaar aan het kenmerk ‘wijze van
    inwinning’ met een domeinwaarde 6.

    In is de eigenschap dat het voorlopige perceelsgrenzen betreft vastgelegd
    als objectbelemmering: “VK: VOORLOPIGE
    KADASTRALE GRENS EN OPPERVLAKTE”.

    Deze werkwijze impliceert dat het fenomeen 'deelpercelen' op termijn zal
    verdwijnen.

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/objectklasse-1/)
    """

    queryset = (models.KadastraalObject.objects
                .select_related('sectie', 'kadastrale_gemeente')
                .all())

    queryset_detail = (
        models.KadastraalObject.objects.select_related(
            'sectie',
            'kadastrale_gemeente',
            'kadastrale_gemeente__gemeente',
            'voornaamste_gerechtigde',
        )
    )

    filter_class = KadastraalObjectFilter

    lookup_value_regex = '[^/]+'

    def get_serializer_class(self):
        if self.action == 'list' or self.action is None:
            return serializers.KadastraalObject

        elif self.action == 'retrieve':

            if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO):
                return serializers.KadastraalObjectDetail

            return serializers.KadastraalObjectDetailPublic


class KadastraalObjectViewSetExpand(KadastraalObjectViewSet):

    queryset = (
        models.KadastraalObject.objects
        .select_related(
            'sectie',
            'voornaamste_gerechtigde',
            'kadastrale_gemeente',
            'kadastrale_gemeente__gemeente')
        .prefetch_related(
            'a_percelen',
            'g_percelen',
            'aantekeningen',
            'beperkingen',
        )
    )

    filter_class = KadastraalObjectFilter

    pagination_class = rest.LimitedHALPagination

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO):
                return serializers.KadastraalObjectDetailExpand
            return serializers.KadastraalObjectDetailExpandPublic

        elif self.action == 'retrieve':
            if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO):
                return serializers.KadastraalObjectDetailExpand
            return serializers.KadastraalObjectDetailExpandPublic


class ZakelijkRechtFilter(FilterSet):
    """
    Filter aantekeningen with better form
    """
    kadastraal_object = filters.CharFilter(method="zakelijkrecht_filter")
    kadastraal_subject = filters.CharFilter(method="zakelijkrecht_filter")

    verblijfsobject = filters.CharFilter(method="vbo_filter", label='vbo')
    verblijfsobjecten__id = filters.CharFilter(method="vbo_filter")
    verblijfsobjecten__landelijk_id = filters.CharFilter(method="vbo_filter")

    class Meta:
        model = models.ZakelijkRecht
        fields = [
            'verblijfsobjecten__landelijk_id',
            'verblijfsobjecten__id',
            'verblijfsobjecten__buurt',
            'verblijfsobject',
            'aard_zakelijk_recht',

            'kadastraal_object',
            'kadastraal_subject',
            'kadastraal_subject__type',
        ]

    def zakelijkrecht_filter(self, queryset, filter_name, value):
        kwargs = { filter_name:value }
        if filter_name == 'kadastraal_subject':
            try:
                subject = models.KadastraalSubject.objects.get(pk=value)
            except models.KadastraalSubject.DoesNotExist:
                subject = None
            if not subject or (subject.type == models.KadastraalSubject.SUBJECT_TYPE_NATUURLIJK and \
                    not self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RSN) ) or \
                    not self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
                raise NotAuthenticated;
        elif filter_name == 'kadastraal_object' and not self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO):
            raise NotAuthenticated;

        filtered = queryset.filter(**kwargs)
        return filtered

    def vbo_filter(self, queryset, _filter_name, value):

        if len(value) == 16:
            return queryset.filter(verblijfsobjecten__landelijk_id=value)

        return queryset.filter(verblijfsobjecten__id=value)


class ZakelijkRechtViewSet(DatapuntViewSet):
    """
    Zakelijkrecht

    Een recht is een door een complex van rechtsregels verleende en
    beschermende bevoegdheid van een persoon.

    Het meest omvattende recht dat een persoon op een zaak kan hebben is de
    eigendom (art. 5:1 BW).

    Uit dit recht kunnen beperkte rechten worden afgeleid en hiermee worden
    bezwaard (art. 3:8 BW).

    Beperkte rechten zijn te vinden in de boeken 3 en 5 BW. (erfpacht, opstal,
    vruchtgebruik), zijn rechten van voor
    1992 (beklemrecht en zakelijk recht als bedoeld in de Belemmeringenwet
    privaatrecht) en zijn oud vaderlandse
    rechten (bijv. visrechten, grondrente enz).

    Een Recht kan ook een oudhollandsrecht zijn.

    [Stelselpedia]
    (http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/objectklasse-7/)
    """
    queryset = (
        models.ZakelijkRecht.objects.select_related(
            'aard_zakelijk_recht',
            'kadastraal_subject')
        .all()
        .order_by(
            'aard_zakelijk_recht__code',
            '_kadastraal_subject_naam')
    )

    serializer_class = serializers.ZakelijkRecht
    serializer_detail_class = serializers.ZakelijkRechtDetail

    filter_class = ZakelijkRechtFilter

    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        """
        Depending on authorisation return subjects

        only plus users can see natuurlijke personen
        """

        # find all items but not natuurlijke personen
        if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO) or \
                self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return self.queryset

        # return empty qs
        return self.queryset.none()

    @detail_route(methods=['get'])
    def subject(self, request, pk=None, *args, **kwargs):

        if not self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return Response(status=HTTP_401_UNAUTHORIZED)

        zakelijk_recht = self.get_object()
        subject = zakelijk_recht.kadastraal_subject

        serializer = serializers.KadastraalSubjectDetailWithPersonalData(
            instance=subject, context=dict(request=request)
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO) or \
                self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return super().list(request, *args, **kwargs)
        return Response(status=HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        if self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RO) or \
                self.request.is_authorized_for(authorization_levels.SCOPE_BRK_RS):
            return super().retrieve(request, *args, **kwargs)

        return Response(status=HTTP_401_UNAUTHORIZED)


class AantekeningenFilter(FilterSet):
    """
    Filter aantekeningen with better form
    """
    # aard_aantekening = django_filters.CharFilter()
    opgelegd_door = filters.CharFilter()
    kadastraal_object = filters.CharFilter()

    class Meta:
        model = models.Aantekening
        fields = [
            'aantekening_id',
            'aard_aantekening',
            'opgelegd_door',
            'kadastraal_object'
        ]


class AantekeningViewSet(DatapuntViewSet):
    """
    Aantekening

    Een Aantekening Kadastraal Object vormt de relatie tussen een Stukdeel en
    een Kadastraal Object en geeft aanvullende informatie over een bestaand
    feit, genoemd in een stuk, dat betrekking heeft op een object en dat
    gevolgen kan hebben voor de uitoefening van rechten op het object.

    LET OP. Aantekening_id SAMEN met subject is uniek.
    het ID veld is gegenereerd.

    [Stelselpedia]
    (https://www.amsterdam.nl/stelselpedia/brk-index/catalog-brk-levering/objectklasse-aant/)
    """
    queryset = (models.Aantekening.objects
                .select_related('aard_aantekening', 'opgelegd_door')
                .all().order_by('aantekening_id'))

    queryset_detail = (
        models.Aantekening.objects.select_related(
            'aard_aantekening', 'opgelegd_door',
            'kadastraal_object', 'kadastraal_object__sectie',
            'kadastraal_object__kadastrale_gemeente')
    )

    serializer_class = serializers.Aantekening
    serializer_detail_class = serializers.AantekeningDetail

    filter_class = AantekeningenFilter

    lookup_value_regex = '[^/]+'

    def get_object(self):
        pk = self.kwargs['pk']
        if pk.isdigit():
            # django id.
            obj = get_object_or_404(models.Aantekening, pk=pk)
        else:
            # official brk id.
            # which is not always unique..
            obj = get_object_or_404(models.Aantekening, aantekening_id=pk)
        return obj


class KadastraalObjectWkpbView(DatapuntViewSet):
    """
    Kadastraal object met extra wkpb informatie

    not publiek
    employee zonder rechten
    plus - all
    """
    queryset = (
        models.KadastraalObject.objects.select_related(
            'sectie',
            'kadastrale_gemeente',
            'kadastrale_gemeente__gemeente',
            'voornaamste_gerechtigde',
        )
    )

    def get_serializer_class(self):
        if self.request.is_authorized_for(authorization_levels.SCOPE_WKPB_RBDU):
            return custom_serializers.KadastraalObjectDetailWkpb
        return custom_serializers.KadastraalObjectDetailWkpbPublic
