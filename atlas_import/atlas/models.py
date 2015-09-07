from django.db import models
from django.contrib.gis.db import models as geo
from django.contrib.postgres.fields import ArrayField

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



# Wkpb

class Beperkingcode(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    """
    Kadastrale code voor de type beperking.
    """

    def __str__(self):
        return "Beperkingcode({})".format(self.code)

class WkpbBroncode(ImportStatusMixin, CodeOmschrijvingMixin, models.Model):
    """
    Het orgaan dat de beperking heeft opgelegd.
    """

    def __str__(self):
        return "WkpbBroncode({})".format(self.code)
    
class WkpbBrondocument(ImportStatusMixin, models.Model):
    """
    Het document dat aan de beperking ten grondslag ligt.
    """

    id = models.IntegerField(null=False, primary_key=True)
    documentnummer = models.IntegerField(null=False)
    bron = models.ForeignKey(WkpbBroncode, null=True)
    documentnaam = models.CharField(max_length=21, null=False)
    persoonsgegeven_afschermen = models.BooleanField(null=False)
    soort_besluit = models.CharField(max_length=60, null=True)

    def __str__(self):
        return "WkpbBrondocument({})".format(self.code)
   
class Beperking(ImportStatusMixin, models.Model):
    """
    Beperking van de eigendom, zoals door een publiekrechtelijke beperking als beschermd monument of een aanschrijving op
    grond van de Woningwet.
    
    http://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/beperking/
    """
   
    id = models.IntegerField(null=False, primary_key=True)
    inschrijfnummer = models.IntegerField(null=False)
    beperkingtype = models.ForeignKey(Beperkingcode, null=False)
    datum_in_werking = models.DateField(null=False)
    datum_einde = models.DateField(null=True)

    def __str__(self):
        return "Beperking({})".format(self.id)

class BeperkingKadastraalObject(ImportStatusMixin, models.Model):
    """
    n:n-relaties: Beperking <> LkiKadastraalObject
    """
    
    id = models.CharField(max_length=33, null=False, primary_key=True)
    beperking = models.ForeignKey('Beperking', null=False)
    kadastraal_object = models.ForeignKey('LkiKadastraalObject', null=False)
    
    def __str__(self):
        return "BeperkingKadastraalObject({})".format(self.id)



# Kadaster

class LkiGemeente(ImportStatusMixin, models.Model):
    """
    Een gemeente is een afgebakend gedeelte van het grondgebied van Nederland, ingesteld op basis van artikel 123 van de Grondwet. 
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    
    id = models.BigIntegerField(null=False, primary_key=True)
    gemeentecode = models.IntegerField(null=False)
    gemeentenaam = models.CharField(max_length=9)
    geometrie = geo.MultiPolygonField(srid=28992, null=True)
    objects = geo.GeoManager()

    def __str__(self):
        return "LkiGemeente({})".format(self.id)


class LkiKadastraleGemeente(ImportStatusMixin, models.Model):
    """
    De kadastrale gemeente is het eerste gedeelte van de aanduiding van een kadastraal perceel.  
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    
    id = models.BigIntegerField(null=False, primary_key=True)
    code = models.CharField(max_length=5, null=False)
    ingang_cyclus = models.DateField(null=False)
    geometrie = geo.MultiPolygonField(srid=28992, null=True)
    objects = geo.GeoManager()

    def __str__(self):
        return "LkiKadastraleGemeente({})".format(self.id)


class LkiSectie(ImportStatusMixin, models.Model):
    """
    Een sectie is een onderdeel van een kadastrale gemeente en als zodanig een onderdeel van de
    kadastrale aanduiding waarbinnen uniek genummerde percelen zijn gelegen.  
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    
    id = models.BigIntegerField(null=False, primary_key=True)
    kadastrale_gemeente_code = models.CharField(max_length=5, null=False)
    code = models.CharField(max_length=2, null=False)
    ingang_cyclus = models.DateField(null=False)
    geometrie = geo.MultiPolygonField(srid=28992, null=True)
    objects = geo.GeoManager()

    def __str__(self):
        return "LkiSectie({})".format(self.id)


class LkiKadastraalObject(ImportStatusMixin, models.Model):
    """
    Een kadastraal object een onroerende zaak of een appartementsrecht waarvoor bij overdracht
    of vestiging van rechten inschrijving in de openbare registers van het Kadaster is vereist.   
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """
    
    id = models.BigIntegerField(null=False, primary_key=True)
    kadastrale_gemeente_code = models.CharField(max_length=5, null=False)
    sectie_code = models.CharField(max_length=2, null=False)
    perceelnummer = models.IntegerField(null=False)
    indexletter = models.CharField(max_length=1, null=False)
    indexnummer = models.IntegerField(null=False)
    oppervlakte = models.IntegerField(null=False)
    ingang_cyclus = models.DateField(null=False)
    aanduiding = models.CharField(max_length=17, null=False, db_index=True)
    geometrie = geo.MultiPolygonField(srid=28992, null=False)
    objects = geo.GeoManager()

    def __str__(self):
        return "LkiKadastraalObject({})".format(self.id)









