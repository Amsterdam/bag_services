from django.db import models
from django.contrib.gis.db import models as geo


class ImportStatusMixin(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DocumentStatusMixin(models.Model):
    document_mutatie = models.DateField(null=True)
    document_nummer = models.CharField(max_length=20, null=True)

    class Meta:
        abstract = True


class CodeOmschrijvingMixin(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        abstract = True


class Bron(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Bron({})".format(self.code)


class Status(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Status({})".format(self.code)


class RedenAfvoer(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Afvoer({})".format(self.code)


class Eigendomsverhouding(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Eigendomsverhouding({})".format(self.code)


class Financieringswijze(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Financieringswijze({})".format(self.code)


class Ligging(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Ligging({})".format(self.code)


class Gebruik(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Gebruik({})".format(self.code)


class LocatieIngang(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "LocatieIngang({})".format(self.code)


class Toegang(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    def __str__(self):
        return "Toegang({})".format(self.code)


class Gemeente(ImportStatusMixin, models.Model):
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=40)
    verzorgingsgebied = models.BooleanField(default=False)
    vervallen = models.BooleanField(default=False)

    def __str__(self):
        return "Gemeente({}, {})".format(self.id, self.naam)


class Woonplaats(ImportStatusMixin, DocumentStatusMixin, models.Model):
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=80)
    naam_ptt = models.CharField(max_length=18, null=True)
    vervallen = models.BooleanField(default=False)
    gemeente = models.ForeignKey(Gemeente)

    def __str__(self):
        return "Woonplaats({}, {})".format(self.id, self.naam)


class Stadsdeel(ImportStatusMixin, models.Model):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van een stadsdeel, ressorterend onder een stadsdeelbestuur.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    gemeente = models.ForeignKey(Gemeente)

    def __str__(self):
        return "Stadsdeel({}, {})".format(self.id, self.naam)


class Buurt(ImportStatusMixin, models.Model):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen zo veel mogelijk gebaseerd zijn op topografische
    elementen.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.BooleanField(default=False)
    stadsdeel = models.ForeignKey(Stadsdeel)

    def __str__(self):
        return "Buurt({}, {})".format(self.id, self.naam)


class OpenbareRuimte(ImportStatusMixin, DocumentStatusMixin, models.Model):
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
    type = models.CharField(max_length=2, null=True, choices=TYPE_CHOICES)
    naam = models.CharField(max_length=150)
    code = models.CharField(max_length=5, unique=True)
    straat_nummer = models.CharField(max_length=10, null=True)
    naam_nen = models.CharField(max_length=24)
    naam_ptt = models.CharField(max_length=17)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    woonplaats = models.ForeignKey(Woonplaats)

    def __str__(self):
        return "Openbare Ruimte({}, {})".format(self.id, self.code)


class Nummeraanduiding(ImportStatusMixin, DocumentStatusMixin, models.Model):
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
    code = models.CharField(max_length=14, unique=True)
    huisnummer = models.CharField(max_length=5)
    huisletter = models.CharField(max_length=1, null=True)
    huisnummer_toevoeging = models.CharField(max_length=4, null=True)
    postcode = models.CharField(max_length=6, null=True)
    type = models.CharField(max_length=2, null=True, choices=OBJECT_TYPE_CHOICES)
    adres_nummer = models.CharField(max_length=10, null=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    openbare_ruimte = models.ForeignKey(OpenbareRuimte)


class Ligplaats(ImportStatusMixin, DocumentStatusMixin, models.Model):
    """
    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen plaats in het water
    al dan niet aangevuld met een op de oever aanwezig terrein of een gedeelte daarvan,
    die bestemd is voor het permanent afmeren van een voor woon-, bedrijfsmatige of recreatieve doeleinden geschikt
    vaartuig.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/
    """

    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14, unique=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True)
    geometrie = geo.PolygonField(null=True, srid=28992)
    hoofdadres = models.ForeignKey(Nummeraanduiding, null=True, related_name="ligplaatsen")

    objects = geo.GeoManager()

    def __str__(self):
        return "Ligplaats({}, {})".format(self.id, self.identificatie)


class Standplaats(ImportStatusMixin, DocumentStatusMixin, models.Model):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig aangewezen terrein of gedeelte daarvan
    dat bestemd is voor het permanent plaatsen van een niet direct en niet duurzaam met de aarde verbonden en voor
    woon-, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/
    """

    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14, unique=True)
    vervallen = models.BooleanField(default=False)
    bron = models.ForeignKey(Bron, null=True)
    status = models.ForeignKey(Status, null=True)
    buurt = models.ForeignKey(Buurt, null=True)
    geometrie = geo.PolygonField(null=True, srid=28992)
    hoofdadres = models.ForeignKey(Nummeraanduiding, null=True, related_name="standplaatsen")

    objects = geo.GeoManager()

    def __str__(self):
        return "Standplaats({}, {})".format(self.id, self.identificatie)


