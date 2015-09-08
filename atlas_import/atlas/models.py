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
    kadastraal_object = models.ForeignKey('lki.KadastraalObject', null=False)
    
    def __str__(self):
        return "BeperkingKadastraalObject({})".format(self.id)










