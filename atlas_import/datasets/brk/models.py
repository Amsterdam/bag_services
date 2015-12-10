from django.contrib.gis.db import models as geo
from django.db import models
from datasets.bag import models as bag

from datasets.generic import mixins


class Gemeente(mixins.ImportStatusMixin):
    gemeente = models.CharField(max_length=50, primary_key=True)

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"


class KadastraleGemeente(mixins.ImportStatusMixin):
    id = models.CharField(max_length=200, primary_key=True)
    gemeente = models.ForeignKey(Gemeente, related_name="kadastrale_gemeentes")

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Kadastrale Gemeente"
        verbose_name_plural = "Kadastrale Gemeentes"


class KadastraleSectie(mixins.ImportStatusMixin):
    id = models.CharField(max_length=200, primary_key=True)

    sectie = models.CharField(max_length=2)
    kadastrale_gemeente = models.ForeignKey(KadastraleGemeente, related_name="secties")

    geometrie = geo.MultiPolygonField(srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Kadastrale Sectie"
        verbose_name_plural = "Kadastrale Secties"


class KadasterCodeOmschrijving(mixins.ImportStatusMixin):
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


class VertrekLand(KadasterCodeOmschrijving):
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
    postbus_nummer = models.IntegerField(null=True)
    postbus_postcode = models.CharField(max_length=50, null=True)
    postbus_woonplaats = models.CharField(max_length=80, null=True)

    buitenland_adres = models.CharField(max_length=100, null=True)
    buitenland_woonplaats = models.CharField(max_length=100, null=True)
    buitenland_regio = models.CharField(max_length=100, null=True)
    buitenland_naam = models.CharField(max_length=100, null=True)
    buitenland_land = models.ForeignKey(Land, null=True)


class KadastraalSubject(mixins.ImportStatusMixin):
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
    bsn = models.CharField(max_length=50, null=True)

    voornamen = models.CharField(max_length=200, null=True)
    voorvoegsels = models.CharField(max_length=10, null=True)
    naam = models.CharField(max_length=200, null=True)
    geslacht = models.ForeignKey(Geslacht, null=True)
    aanduiding_naam = models.ForeignKey(AanduidingNaam, null=True)
    geboortedatum = models.DateField(null=True)
    geboorteplaats = models.CharField(max_length=80)
    geboorteland = models.ForeignKey(Land, null=True)
    overlijdensdatum = models.DateField(null=True)

    partner_voornamen = models.CharField(max_length=200)
    partner_voorvoegsels = models.CharField(max_length=10)
    partner_naam = models.CharField(max_length=200)

    land_waarnaar_vertrokken = models.ForeignKey(VertrekLand, null=True)

    rsin = models.CharField(max_length=80, null=True)
    kvknummer = models.CharField(max_length=8, null=True)
    rechtsvorm = models.ForeignKey(Rechtsvorm, null=True)
    statutaire_naam = models.CharField(max_length=200, null=True)
    statutaire_zetel = models.CharField(max_length=24, null=True)

    bron = models.SmallIntegerField(choices=BRON_CHOICES)
    woonadres = models.ForeignKey(Adres, null=True, related_name="woonadres")
    postadres = models.ForeignKey(Adres, null=True, related_name="postadres")


class SoortGrootte(KadasterCodeOmschrijving):
    pass


class CultuurCodeOnbebouwd(KadasterCodeOmschrijving):
    pass


class CultuurCodeBebouwd(KadasterCodeOmschrijving):
    pass


class KadastraalObject(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aanduiding = models.CharField(max_length=16)
    gemeente = models.ForeignKey(Gemeente, related_name="kadastrale_objecten")
    kadastrale_gemeente = models.ForeignKey(KadastraleGemeente, related_name="kadastrale_objecten")
    sectie = models.ForeignKey(KadastraleSectie, related_name="kadastrale_objecten")
    perceelnummer = models.IntegerField()
    index_letter = models.CharField(max_length=1)
    index_nummer = models.IntegerField()
    soort_grootte = models.ForeignKey(SoortGrootte, null=True)
    grootte = models.IntegerField()
    g_perceel = models.ForeignKey('KadastraalObject', null=True, related_name="a_percelen")
    koopsom = models.IntegerField(null=True)
    koopsom_valuta_code = models.CharField(max_length=50, null=True)
    koopjaar = models.CharField(max_length=15, null=True)
    meer_objecten = models.BooleanField(default=False)
    cultuurcode_onbebouwd = models.ForeignKey(CultuurCodeOnbebouwd)
    cultuurcode_bebouwd = models.ForeignKey(CultuurCodeBebouwd)

    register9_tekst = models.TextField()
    status_code = models.CharField(max_length=50)
    toestandsdatum = models.DateField()
    voorlopige_kadastrale_grens = models.BooleanField(default=False)
    in_onderzoek = models.TextField(null=True)

    geometrie = geo.MultiPolygonField(srid=28992, null=True)
    voornaamste_gerechtigde = models.ForeignKey(KadastraalSubject)
    verblijfsobjecten = models.ManyToManyField(bag.Verblijfsobject, through='KadastraalObjectVerblijfsobjectRelatie')

    objects = geo.GeoManager()


class KadastraalObjectVerblijfsobjectRelatie(mixins.ImportStatusMixin):
    id = models.UUIDField(primary_key=True)
    kadastraal_object = models.ForeignKey(KadastraalObject)
    verblijfsobject = models.ForeignKey(bag.Verblijfsobject, null=True)


class AardZakelijkRecht(KadasterCodeOmschrijving):
    pass


class AppartementsrechtsSplitsType(KadasterCodeOmschrijving):
    pass


class ZakelijkRecht(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aard_zakelijk_recht = models.ForeignKey(AardZakelijkRecht, null=True)
    aard_zakelijk_recht_akr = models.CharField(max_length=3, null=True)

    belast_azt = models.CharField(max_length=15)
    belast_met_azt = models.CharField(max_length=15)
    ontstaan_uit = models.ForeignKey('ZakelijkRecht', null=True, related_name="ontstaan_uit_set")
    betrokken_bij = models.ForeignKey('ZakelijkRecht', null=True, related_name="betrokken_bij_set")

    beperkt_tot_tng = models.BooleanField(default=False)

    kadastraal_object = models.ForeignKey(KadastraalObject, related_name="rechten")
    kadastraal_subject = models.ForeignKey(KadastraalSubject, related_name="rechten")

    kadastraal_object_status = models.CharField(max_length=50)

    app_rechtsplitstype = models.ForeignKey(AppartementsrechtsSplitsType, null=True)


class AardAantekening(KadasterCodeOmschrijving):
    pass


class Aantekening(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aard_aantekening = models.ForeignKey(AardAantekening)
    omschrijving = models.TextField()
    type = models.CharField(max_length=33)

    kadastraal_object = models.ForeignKey(KadastraalObject, null=True, related_name="aantekeningen")
    zekerheidsrecht = models.ForeignKey(ZakelijkRecht, null=True, related_name="aantekeningen")
    kadastraal_subject = models.ForeignKey(KadastraalSubject, null=True, related_name="aantekeningen")


class AardStukdeel(KadasterCodeOmschrijving):
    pass


class RegisterCode(KadasterCodeOmschrijving):
    pass


class SoortRegister(KadasterCodeOmschrijving):
    pass


class Stukdeel(mixins.ImportStatusMixin):
    id = models.CharField(max_length=60, primary_key=True)
    aard_stukdeel = models.ForeignKey(AardStukdeel)
    koopsom = models.IntegerField()
    koopsom_valuta = models.CharField(max_length=50)

    stuk_id = models.CharField(max_length=60)
    portefeuille_nummer = models.CharField(max_length=16)
    tijdstip_aanbieding = models.DateTimeField()
    reeks_code = models.CharField(max_length=50)
    volgnummer = models.IntegerField()
    register_code = models.ForeignKey(RegisterCode)
    soort_register = models.ForeignKey(SoortRegister)

    deel_soort = models.CharField(max_length=5)

    tenaamstelling = models.ForeignKey(ZakelijkRecht)
    aantekening = models.ForeignKey(Aantekening)

