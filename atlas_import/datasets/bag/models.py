from django.contrib.gis.db import models as geo
from django.db import models

from datasets.generic import mixins


class Bron(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronnen"


class Status(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


class RedenAfvoer(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Reden Afvoer"
        verbose_name_plural = "Reden Afvoer"


class Eigendomsverhouding(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Eigendomsverhouding"
        verbose_name_plural = "Eigendomsverhoudingen"


class Financieringswijze(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Financieringswijze"
        verbose_name_plural = "Financieringswijzes"


class Ligging(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Ligging"
        verbose_name_plural = "Ligging"


class Gebruik(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Gebruik"
        verbose_name_plural = "Gebruik"


class LocatieIngang(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Locatie Ingang"
        verbose_name_plural = "Locaties Ingang"


class Toegang(mixins.ImportStatusMixin, mixins.CodeOmschrijvingMixin, models.Model):
    class Meta:
        verbose_name = "Toegang"
        verbose_name_plural = "Toegang"


class Gemeente(mixins.ImportStatusMixin, models.Model):
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=40)
    verzorgingsgebied = models.BooleanField(default=False)
    vervallen = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"

    def __str__(self):
        return self.naam


class Woonplaats(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                 mixins.DocumentStatusMixin, models.Model):
    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=80)
    naam_ptt = models.CharField(max_length=18, null=True)
    vervallen = models.BooleanField(default=False)
    gemeente = models.ForeignKey(Gemeente, related_name='woonplaatsen')

    class Meta:
        verbose_name = "Woonplaats"
        verbose_name_plural = "Woonplaatsen"

    def __str__(self):
        return self.naam


class Hoofdklasse(mixins.ImportStatusMixin, models.Model):
    """
    De hoofdklasse is een abstracte klasse waar sommige andere gebiedsklassen, zoals stadsdeel en buurt, van afstammen.
    Deze afstammelingen erven alle kenmerken over van deze hoofdklasse. Het kenmerk 'diva_id' komt bijvoorbeeld voor
    bij alle gebieden.
    """

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        abstract = True


class Stadsdeel(Hoofdklasse):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van een stadsdeel, ressorterend onder een stadsdeelbestuur.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    gemeente = models.ForeignKey(Gemeente, related_name='stadsdelen')

    class Meta:
        verbose_name = "Stadsdeel"
        verbose_name_plural = "Stadsdelen"

    def __str__(self):
        return self.naam


class Buurt(Hoofdklasse):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen zo veel mogelijk gebaseerd zijn op topografische
    elementen.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    stadsdeel = models.ForeignKey(Stadsdeel, related_name='buurten')

    class Meta:
        verbose_name = "Buurt"
        verbose_name_plural = "Buurten"

    def __str__(self):
        return self.naam


class Bouwblok(Hoofdklasse):
    """
    Een bouwblok is het kleinst mogelijk afgrensbare gebied, in zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen en/of waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)  # Bouwbloknummer
    buurt = models.ForeignKey(Buurt, related_name='bouwblokken', null=True)
    ingang_cyclus = models.DateField(null=True)

    class Meta:
        verbose_name = "Bouwblok"
        verbose_name_plural = "Bouwblokken"

    def __str__(self):
        return "{}".format(self.code)


class OpenbareRuimte(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                     mixins.DocumentStatusMixin, models.Model):
    """
    Een OPENBARE RUIMTE is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen en van een naam voorziene
    buitenruimte die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water, terrein, spoorbaan en landschappelijk gebied.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-3/
    """
    TYPE_WEG = '01'
    TYPE_WATER = '02'
    TYPE_SPOORBAAN = '03'
    TYPE_TERREIN = '04'
    TYPE_KUNSTWERK = '05'
    TYPE_LANDSCHAPPELIJK_GEBIED = '06'
    TYPE_ADMINISTRATIEF_GEBIED = '07'

    TYPE_CHOICES = (
        (TYPE_WEG, 'Weg'),
        (TYPE_WATER, 'Water'),
        (TYPE_SPOORBAAN, 'Spoorbaan'),
        (TYPE_TERREIN, 'Terrein'),
        (TYPE_KUNSTWERK, 'Kunstwerk'),
        (TYPE_LANDSCHAPPELIJK_GEBIED, 'Landschappelijk gebied'),
        (TYPE_ADMINISTRATIEF_GEBIED, 'Administratief gebied'),
    )

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    type = models.CharField(max_length=2, null=True, choices=TYPE_CHOICES)
    naam = models.CharField(max_length=150)
    code = models.CharField(max_length=5, unique=True)
    straat_nummer = models.CharField(max_length=10, null=True)
    naam_nen = models.CharField(max_length=24)
    naam_ptt = models.CharField(max_length=17)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    woonplaats = models.ForeignKey(Woonplaats, related_name="openbare_ruimtes")

    class Meta:
        verbose_name = "Openbare Ruimte"
        verbose_name_plural = "Openbare Ruimtes"

    def __str__(self):
        return self.naam


class Nummeraanduiding(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                       mixins.DocumentStatusMixin, models.Model):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject, standplaats of ligplaats.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-2/
    """

    OBJECT_TYPE_VERBLIJFSOBJECT = '01'
    OBJECT_TYPE_STANDPLAATS = '02'
    OBJECT_TYPE_LIGPLAATS = '03'
    OBJECT_TYPE_OVERIG_GEBOUWD = '04'
    OBJECT_TYPE_OVERIG_TERREIN = '05'

    OBJECT_TYPE_CHOICES = (
        (OBJECT_TYPE_VERBLIJFSOBJECT, 'Verblijfsobject'),
        (OBJECT_TYPE_STANDPLAATS, 'Standplaats'),
        (OBJECT_TYPE_LIGPLAATS, 'Ligplaats'),
        (OBJECT_TYPE_OVERIG_GEBOUWD, 'Overig gebouwd object'),
        (OBJECT_TYPE_OVERIG_TERREIN, 'Overig terrein'),
    )

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    huisnummer = models.IntegerField()
    huisletter = models.CharField(max_length=1, null=True)
    huisnummer_toevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    type = models.CharField(max_length=2, null=True, choices=OBJECT_TYPE_CHOICES)
    adres_nummer = models.CharField(max_length=10, null=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    openbare_ruimte = models.ForeignKey(OpenbareRuimte, related_name='adressen')

    ligplaats = models.ForeignKey('Ligplaats', null=True, related_name='adressen')
    standplaats = models.ForeignKey('Standplaats', null=True, related_name='adressen')
    verblijfsobject = models.ForeignKey('Verblijfsobject', null=True, related_name='adressen')
    hoofdadres = models.NullBooleanField(default=None)

    class Meta:
        verbose_name = "Nummeraanduiding"
        verbose_name_plural = "Nummeraanduidingen"
        ordering = ('openbare_ruimte__naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging')

    def __str__(self):
        return self.adres()

    def adres(self):
        return (self.openbare_ruimte.naam
                + ' ' + str(self.huisnummer)
                + (self.huisletter if self.huisletter else '')
                + ('-' + self.huisnummer_toevoeging if self.huisnummer_toevoeging else '')
                )


class AdresseerbaarObjectMixin(object):
    @property
    def hoofdadres(self):
        # noinspection PyUnresolvedReferences
        candidates = [a for a in self.adressen.all() if a.hoofdadres]
        return candidates[0] if candidates else None

    @property
    def nevenadressen(self):
        return [a for a in self.adressen.all() if not a.hoofdadres]

    def __str__(self):
        if self.hoofdadres:
            return self.hoofdadres.adres()
        return "adres onbekend"


class Ligplaats(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen plaats in het water
    al dan niet aangevuld met een op de oever aanwezig terrein of een gedeelte daarvan,
    die bestemd is voor het permanent afmeren van een voor woon-, bedrijfsmatige of recreatieve doeleinden geschikt
    vaartuig.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True, related_name='ligplaatsen')
    geometrie = geo.PolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Ligplaats"
        verbose_name_plural = "Ligplaatsen"


class Standplaats(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                  mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een niet direct en niet duurzaam met de aarde verbonden en voor
    woon-, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True, related_name='standplaatsen')
    geometrie = geo.PolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Standplaats"
        verbose_name_plural = "Standplaatsen"


class Verblijfsobject(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin,
                      mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en voor woon-, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen afsluitbare toegang vanaf de
    openbare weg, een erf of een gedeelde verkeersruimte, onderwerp kan zijn van goederenrechtelijke rechtshandelingen
    en in functioneel opzicht zelfstandig is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    gebruiksdoel_code = models.CharField(max_length=4, null=True)
    gebruiksdoel_omschrijving = models.CharField(max_length=150, null=True)
    oppervlakte = models.PositiveIntegerField(null=True)
    bouwlaag_toegang = models.IntegerField(null=True)
    status_coordinaat_code = models.CharField(max_length=3, null=True)
    status_coordinaat_omschrijving = models.CharField(max_length=150, null=True)
    verhuurbare_eenheden = models.PositiveIntegerField(null=True)
    bouwlagen = models.PositiveIntegerField(null=True)
    type_woonobject_code = models.CharField(max_length=2, null=True)
    type_woonobject_omschrijving = models.CharField(max_length=150, null=True)
    woningvoorraad = models.BooleanField(default=False)
    aantal_kamers = models.PositiveIntegerField(null=True)
    vervallen = models.PositiveIntegerField(default=False)
    reden_afvoer = models.ForeignKey(RedenAfvoer, null=True)
    bron = models.ForeignKey(Bron, null=True)
    eigendomsverhouding = models.ForeignKey(Eigendomsverhouding, null=True)
    financieringswijze = models.ForeignKey(Financieringswijze, null=True)
    gebruik = models.ForeignKey(Gebruik, null=True)
    locatie_ingang = models.ForeignKey(LocatieIngang, null=True)
    ligging = models.ForeignKey(Ligging, null=True)
    toegang = models.ForeignKey(Toegang, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True, related_name='verblijfsobjecten')

    panden = models.ManyToManyField('Pand', related_name='verblijfsobjecten', through='VerblijfsobjectPandRelatie')

    geometrie = geo.PointField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Verblijfsobject"
        verbose_name_plural = "Verblijfsobjecten"


class Pand(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin, mixins.ImportStatusMixin, mixins.DocumentStatusMixin,
           models.Model):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en bouwkundig-constructief zelfstandige eenheid die direct
    en duurzaam met de aarde is verbonden en betreedbaar en afsluitbaar is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    bouwjaar = models.PositiveIntegerField(null=True)
    laagste_bouwlaag = models.IntegerField(null=True)
    hoogste_bouwlaag = models.IntegerField(null=True)
    pandnummer = models.CharField(max_length=10, null=True)
    vervallen = models.BooleanField(default=False)
    status = models.ForeignKey(Status, null=True)
    bouwblok = models.ForeignKey(Bouwblok, null=True)

    geometrie = geo.PolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Pand"
        verbose_name_plural = "Panden"

    def __str__(self):
        return "{}".format(self.id)


class VerblijfsobjectPandRelatie(mixins.ImportStatusMixin, models.Model):
    id = models.CharField(max_length=29, primary_key=True)
    pand = models.ForeignKey(Pand)
    verblijfsobject = models.ForeignKey(Verblijfsobject)

    class Meta:
        verbose_name = "Verblijfsobject-Pand relatie"
        verbose_name_plural = "Verblijfsobject-Pand relaties"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pand_id and self.verblijfsobject_id:
            self.id = self.pand_id + '_' + self.verblijfsobject_id

    def __str__(self):
        return "Pand-Verblijfsobject({}-{})".format(self.pand_id, self.verblijfsobject_id)


class Buurtcombinatie(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR', 'DOCDATUM', 'INGSDATUM', 'EINDDATUM']
    """

    naam = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    vollcode = models.CharField(max_length=3)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    ingang_cyclus = models.DateField(null=True)

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Buurtcombinatie"
        verbose_name_plural = "Buurtcombinaties"

    def __str__(self):
        return self.naam


class Gebiedsgerichtwerken(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM', 'CODE', 'STADSDEEL', 'INGSDATUM', 'EINDDATUM', 'DOCNR', 'DOCDATUM']
    """

    naam = models.CharField(max_length=100)
    code = models.CharField(max_length=4)
    stadsdeel = models.ForeignKey(Stadsdeel, related_name='gebiedsgerichtwerken')

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Gebiedsgerichtwerken"
        verbose_name_plural = "Gebiedsgerichtwerken"

    def __str__(self):
        return self.naam


class Grootstedelijkgebied(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    naam = models.CharField(max_length=100)

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Grootstedelijkgebied"
        verbose_name_plural = "Grootstedelijke gebieden"

    def __str__(self):
        return "{}".format(self.naam)


class Unesco(mixins.ImportStatusMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    naam = models.CharField(max_length=100)

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Unesco"
        verbose_name_plural = "Unesco"

    def __str__(self):
        return "{}".format(self.naam)
