from django.db import models
from django.contrib.gis.db import models as geo


class ImportStatusMixin(models.Model):
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Gemeente(ImportStatusMixin, models.Model):
    """
    Een gemeente is een afgebakend gedeelte van het grondgebied van Nederland, ingesteld op basis van artikel 123 van
    de Grondwet.
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """

    id = models.BigIntegerField(null=False, primary_key=True)
    gemeentecode = models.IntegerField(null=False)
    gemeentenaam = models.CharField(max_length=9)
    geometrie = geo.MultiPolygonField(srid=28992, null=True)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"

    def __str__(self):
        return "{}: {}".format(self.gemeentecode, self.gemeentenaam)


class KadastraleGemeente(ImportStatusMixin, models.Model):
    """
    De kadastrale gemeente is het eerste gedeelte van de aanduiding van een kadastraal perceel.  
    
    http://www.amsterdam.nl/stelselpedia/brk-index/catalogus/
    """

    id = models.BigIntegerField(null=False, primary_key=True)
    code = models.CharField(max_length=5, null=False)
    ingang_cyclus = models.DateField(null=False)
    geometrie = geo.MultiPolygonField(srid=28992, null=True)

    objects = geo.GeoManager()

    class Meta:
        verbose_name = "Kadastrale Gemeente"
        verbose_name_plural = "Kadastrale Gemeentes"

    def __str__(self):
        return "{}".format(self.code)


class Sectie(ImportStatusMixin, models.Model):
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

    class Meta:
        verbose_name = "Sectie"
        verbose_name_plural = "Secties"


    def __str__(self):
        return "{}".format(self.code)


class KadastraalObject(ImportStatusMixin, models.Model):
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

    class Meta:
        verbose_name = "Kadastraal Object"
        verbose_name_plural = "Kadastrale Objecten"

    def __str__(self):
        return "{}".format(self.aanduiding)
