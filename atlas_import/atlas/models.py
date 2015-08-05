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

    def __str__(self):
        return "Nummeraanduiding({}, {})".format(self.id, self.code)

    def adres(self):
        return (self.openbare_ruimte.naam
                + ' ' + self.huisnummer
                + (self.huisletter if self.huisletter else '')
                + ('-' + self.huisnummer_toevoeging if self.huisnummer_toevoeging else '')
                )



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


class Verblijfsobject(ImportStatusMixin, DocumentStatusMixin, models.Model):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en voor woon-, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen afsluitbare toegang vanaf de
    openbare weg, een erf of een gedeelde verkeersruimte, onderwerp kan zijn van goederenrechtelijke rechtshandelingen
    en in functioneel opzicht zelfstandig is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/
    """

    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14, unique=True)
    gebruiksdoel_code = models.CharField(max_length=4, null=True)
    gebruiksdoel_omschrijving = models.CharField(max_length=150, null=True)
    oppervlakte = models.PositiveIntegerField(null=True)
    bouwlaag_toegang = models.IntegerField(null=True)
    status_coordinaat_code = models.CharField(max_length=3, null=True)
    status_coordinaat_omschrijving = models.CharField(max_length=150, null=True)
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
    buurt = models.ForeignKey(Buurt, null=True)
    hoofdadres = models.ForeignKey(Nummeraanduiding, null=True, related_name="verblijfsobjecten")
    panden = models.ManyToManyField('Pand', related_name='verblijfsobjecten')

    geometrie = geo.PointField(null=True, srid=28992)

    objects = geo.GeoManager()

    def __str__(self):
        return "Verblijfsobject({}, {})".format(self.id, self.identificatie)


class Pand(ImportStatusMixin, DocumentStatusMixin, models.Model):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en bouwkundig-constructief zelfstandige eenheid die direct
    en duurzaam met de aarde is verbonden en betreedbaar en afsluitbaar is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/
    """

    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14, unique=True)
    bouwjaar = models.PositiveIntegerField(null=True)
    laagste_bouwlaag = models.IntegerField(null=True)
    hoogste_bouwlaag = models.IntegerField(null=True)
    pandnummer = models.CharField(max_length=10, null=True)
    vervallen = models.BooleanField(default=False)
    status = models.ForeignKey(Status, null=True)

    geometrie = geo.PolygonField(null=True, srid=28992)

    objects = geo.GeoManager()

    def __str__(self):
        return "Pand({})".format(self.id)
    
'''    
class Beperking(ImportStatusMixin, models.Model):
    """
    Beperking van de eigendom, zoals door een publiekrechtelijke beperking als beschermd monument of een aanschrijving op
    grond van de Woningwet.
    
    http://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/beperking/
    """
    
    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14, unique=True)
    inschrijfnummer = models.IntegerField(null=False)
    beperkingcode = models.CharField(max_length=2, null=False)
    datum_in_werking = models.DateField(null=False)
    datum_einde = models.DateField(null=True)

    def __str__(self):
        return "Beperking({})".format(self.id)

'''

class Beperkingcode(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):

    def __str__(self):
        return "Beperkingcode({})".format(self.code)

class WkpbBroncode(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):

    def __str__(self):
        return "WkpbBroncode({})".format(self.code)
    
class WkpbBrondocument(ImportStatusMixin, models.Model):

    id = models.IntegerField(null=False, primary_key=True)
    documentnummer = models.IntegerField(null=False)
    bron = models.ForeignKey(WkpbBroncode, null=True)
    documentnaam = models.CharField(max_length=21, null=False)
    persoonsgegeven_afschermen = models.BooleanField(null=False)
    soort_besluit = models.CharField(max_length=60, null=True)

    def __str__(self):
        return "WkpbBrondocument({})".format(self.code)
   



