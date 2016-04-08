import uuid

from django.contrib.gis.db import models as geo
from django.db import models

from datasets.bag import models as bag
from datasets.generic import mixins, kadaster


class Gemeente(mixins.ImportStatusMixin):
    gemeente = models.CharField(max_length=50, primary_key=True)

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"

    def __str__(self):
        return "{}".format(self.gemeente)


class KadastraleGemeente(mixins.ImportStatusMixin):
    id = models.CharField(max_length=200, primary_key=True)
    naam = models.CharField(max_length=100)
    gemeente = models.ForeignKey(Gemeente, related_name="kadastrale_gemeentes")

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Kadastrale Gemeente"
        verbose_name_plural = "Kadastrale Gemeentes"

    def __str__(self):
        return "{}".format(self.id)


class KadastraleSectie(mixins.ImportStatusMixin):
    id = models.CharField(max_length=200, primary_key=True)

    sectie = models.CharField(max_length=2)
    kadastrale_gemeente = models.ForeignKey(KadastraleGemeente, related_name="secties")

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Kadastrale Sectie"
        verbose_name_plural = "Kadastrale Secties"

    def __str__(self):
        return "{}".format(self.id)


class KadasterCodeOmschrijving(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    omschrijving = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class Beschikkingsbevoegdheid(KadasterCodeOmschrijving):
    pass


class Geslacht(KadasterCodeOmschrijving):
    pass


class AanduidingNaam(KadasterCodeOmschrijving):
    pass


class Land(KadasterCodeOmschrijving):
    pass


class Rechtsvorm(KadasterCodeOmschrijving):
    pass


class Adres(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    openbareruimte_naam = models.CharField(max_length=80, null=True)
    huisnummer = models.IntegerField(null=True)
    huisletter = models.CharField(max_length=1, null=True)
    toevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    woonplaats = models.CharField(max_length=80, null=True)

    # todo: apart modelleren?
    postbus_nummer = models.IntegerField(null=True)
    postbus_postcode = models.CharField(max_length=50, null=True)
    postbus_woonplaats = models.CharField(max_length=80, null=True)

    buitenland_adres = models.CharField(max_length=100, null=True)
    buitenland_woonplaats = models.CharField(max_length=100, null=True)
    buitenland_regio = models.CharField(max_length=100, null=True)
    buitenland_naam = models.CharField(max_length=100, null=True)
    buitenland_land = models.ForeignKey(Land, null=True)


class KadastraalSubject(mixins.ImportStatusMixin):
    """
    Een Kadastraal Subject is een persoon die
    in de kadastrale registratie voorkomt.
    Het betreft hier zowel natuurlijk- als niet natuurlijk personen.

    https://www.amsterdam.nl/stelselpedia/brk-index/catalog-brk-levering/kadastraal-subject/
    """
    SUBJECT_TYPE_NATUURLIJK = 0
    SUBJECT_TYPE_NIET_NATUURLIJK = 1
    SUBJECT_TYPE_CHOICES = (
        (SUBJECT_TYPE_NATUURLIJK, "Natuurlijk persoon"),
        (SUBJECT_TYPE_NIET_NATUURLIJK, "Niet-natuurlijk persoon"),
    )

    BRON_REGISTRATIE = 0
    BRON_KADASTER = 1
    BRON_CHOICES = (
        (BRON_REGISTRATIE, "Basisregistraties"),
        (BRON_KADASTER, "Kadaster"),
    )

    id = models.CharField(max_length=60, primary_key=True)
    type = models.SmallIntegerField(choices=SUBJECT_TYPE_CHOICES)
    beschikkingsbevoegdheid = models.ForeignKey(Beschikkingsbevoegdheid, null=True)

    voornamen = models.CharField(max_length=200, null=True)
    voorvoegsels = models.CharField(max_length=10, null=True)
    naam = models.CharField(max_length=200, null=True)
    geslacht = models.ForeignKey(Geslacht, null=True)
    aanduiding_naam = models.ForeignKey(AanduidingNaam, null=True)
    geboortedatum = models.CharField(max_length=50, null=True)  # kadaster-data kan onvolledig zijn
    geboorteplaats = models.CharField(max_length=80, null=True)
    geboorteland = models.ForeignKey(Land, null=True, related_name='+')
    overlijdensdatum = models.CharField(max_length=50, null=True)  # kadaster-data kan onvolledig zijn

    partner_voornamen = models.CharField(max_length=200, null=True)
    partner_voorvoegsels = models.CharField(max_length=10, null=True)
    partner_naam = models.CharField(max_length=200, null=True)

    land_waarnaar_vertrokken = models.ForeignKey(Land, null=True, related_name='+')

    rsin = models.CharField(max_length=80, null=True)
    kvknummer = models.CharField(max_length=8, null=True)
    rechtsvorm = models.ForeignKey(Rechtsvorm, null=True)
    statutaire_naam = models.CharField(max_length=200, null=True)
    statutaire_zetel = models.CharField(max_length=24, null=True)

    bron = models.SmallIntegerField(choices=BRON_CHOICES)
    woonadres = models.ForeignKey(Adres, null=True, related_name="+")
    postadres = models.ForeignKey(Adres, null=True, related_name="+")

    class Meta:
        verbose_name = "Kadastraal subject"
        verbose_name_plural = "Kadastrale subjecten"
        index_together = (
            ('naam', 'statutaire_naam'),
        )

        permissions = (
            ('view_sensitive_details', 'Kan privacy-gevoelige data inzien'),
        )

    def __str__(self):
        return self.volledige_naam()

    def is_natuurlijk_persoon(self):
        return not self.statutaire_naam

    def volledige_naam(self):
        if self.statutaire_naam:
            return self.statutaire_naam

        return " ".join([part for part in (self.voornamen,
                                           self.voorvoegsels,
                                           self.naam) if part])


class SoortGrootte(KadasterCodeOmschrijving):
    pass


class CultuurCodeOnbebouwd(KadasterCodeOmschrijving):
    pass


class CultuurCodeBebouwd(KadasterCodeOmschrijving):
    pass


class APerceelGPerceelRelatie(models.Model):
    id = models.CharField(max_length=121, primary_key=True)
    a_perceel = models.ForeignKey('KadastraalObject', related_name='g_perceel_relaties')
    g_perceel = models.ForeignKey('KadastraalObject', related_name='a_perceel_relaties')


class KadastraalObject(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aanduiding = models.CharField(max_length=17)
    kadastrale_gemeente = models.ForeignKey(KadastraleGemeente, related_name="kadastrale_objecten")
    sectie = models.ForeignKey(KadastraleSectie, related_name="kadastrale_objecten")
    perceelnummer = models.IntegerField()
    index_letter = models.CharField(max_length=1)
    index_nummer = models.IntegerField()
    soort_grootte = models.ForeignKey(SoortGrootte, null=True)
    grootte = models.IntegerField(null=True)
    koopsom = models.IntegerField(null=True)
    koopsom_valuta_code = models.CharField(max_length=50, null=True)
    koopjaar = models.CharField(max_length=15, null=True)
    meer_objecten = models.NullBooleanField(default=None)
    cultuurcode_onbebouwd = models.ForeignKey(CultuurCodeOnbebouwd, null=True)
    cultuurcode_bebouwd = models.ForeignKey(CultuurCodeBebouwd, null=True)

    register9_tekst = models.TextField()
    status_code = models.CharField(max_length=50)
    toestandsdatum = models.DateField(null=True)
    voorlopige_kadastrale_grens = models.NullBooleanField(default=None)
    in_onderzoek = models.TextField(null=True)

    geometrie = geo.MultiPolygonField(srid=28992, null=True)
    geom_point = geo.PointField(srid=28992, null=True)

    voornaamste_gerechtigde = models.ForeignKey(KadastraalSubject, null=True)
    verblijfsobjecten = models.ManyToManyField(bag.Verblijfsobject,
                                               through='KadastraalObjectVerblijfsobjectRelatie',
                                               related_name="kadastrale_objecten")

    g_percelen = models.ManyToManyField('KadastraalObject',
                                        through=APerceelGPerceelRelatie,
                                        through_fields=('a_perceel', 'g_perceel'),
                                        related_name="a_percelen")

    objects = geo.GeoManager()

    class Meta:
        ordering = ('kadastrale_gemeente__id', 'sectie', 'perceelnummer', '-index_letter', 'index_nummer')

    def __str__(self):
        return self.get_aanduiding_spaties()

    def get_aanduiding_spaties(self):
        return kadaster.get_aanduiding_spaties(
                self.kadastrale_gemeente.id, self.sectie.sectie, self.perceelnummer,
                self.index_letter, self.index_nummer
        )


class KadastraalObjectVerblijfsobjectRelatie(mixins.ImportStatusMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    kadastraal_object = models.ForeignKey(KadastraalObject)
    verblijfsobject = models.ForeignKey(bag.Verblijfsobject, null=True)


class AardZakelijkRecht(KadasterCodeOmschrijving):
    pass


class AppartementsrechtsSplitsType(KadasterCodeOmschrijving):
    pass


class ZakelijkRecht(mixins.ImportStatusMixin):
    id = models.CharField(max_length=183, primary_key=True)
    zrt_id = models.CharField(max_length=60)
    aard_zakelijk_recht = models.ForeignKey(AardZakelijkRecht, null=True)
    aard_zakelijk_recht_akr = models.CharField(max_length=3, null=True)

    ontstaan_uit = models.ForeignKey(KadastraalSubject, null=True, related_name="ontstaan_uit_set")
    betrokken_bij = models.ForeignKey(KadastraalSubject, null=True, related_name="betrokken_bij_set")

    teller = models.IntegerField(null=True)
    noemer = models.IntegerField(null=True)

    kadastraal_object = models.ForeignKey(KadastraalObject, related_name="rechten")
    kadastraal_subject = models.ForeignKey(KadastraalSubject, related_name="rechten")

    kadastraal_object_status = models.CharField(max_length=50)

    app_rechtsplitstype = models.ForeignKey(AppartementsrechtsSplitsType, null=True)

    verblijfsobjecten = models.ManyToManyField(bag.Verblijfsobject,
                                               through='ZakelijkRechtVerblijfsobjectRelatie',
                                               related_name="rechten")

    _kadastraal_subject_naam = models.CharField(max_length=200)
    _kadastraal_object_aanduiding = models.CharField(max_length=100)

    def __str__(self):
        omschrijving = self.aard_zakelijk_recht.omschrijving if self.aard_zakelijk_recht else ''
        aandeel = '({}/{})'.format(self.teller,
                                   self.noemer) if self.teller is not None and self.noemer is not None else ''

        return "{} - {}{} - {}".format(self._kadastraal_subject_naam, omschrijving, aandeel,
                                       self._kadastraal_object_aanduiding)


class ZakelijkRechtVerblijfsobjectRelatie(models.Model):
    zakelijk_recht = models.ForeignKey(ZakelijkRecht)
    verblijfsobject = models.ForeignKey(bag.Verblijfsobject)


class AardAantekening(KadasterCodeOmschrijving):
    pass


class Aantekening(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aard_aantekening = models.ForeignKey(AardAantekening)
    omschrijving = models.TextField()

    kadastraal_object = models.ForeignKey(KadastraalObject, null=True, related_name="aantekeningen")
    opgelegd_door = models.ForeignKey(KadastraalSubject, null=True, related_name="aantekeningen")

    def __str__(self):
        return self.aard_aantekening.omschrijving if self.aard_aantekening.omschrijving else self.id
