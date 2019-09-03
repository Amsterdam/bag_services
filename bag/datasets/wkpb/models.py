from django.db import models

from bag.settings import settings
from datasets.bag import models as bag
from datasets.brk import models as brk
from datasets.generic import mixins


# Wkpb


class Beperkingcode(mixins.CodeOmschrijvingMixin, models.Model):
    """
    Kadastrale code voor de type beperking.
    """

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Beperkingcode"
        verbose_name_plural = "Beperkingcodes"

    def __str__(self):
        return self.omschrijving


class Broncode(mixins.CodeOmschrijvingMixin, models.Model):
    """
    Het orgaan dat de beperking heeft opgelegd.
    """

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Broncode"
        verbose_name_plural = "Broncodes"

    def __str__(self):
        return self.omschrijving


class Beperking(models.Model):
    """
    Beperking van de eigendom, zoals door een publiekrechtelijke
    beperking als beschermd monument of een aanschrijving op
    grond van de Woningwet.

    http://www.amsterdam.nl/stelselpedia/wkpb-index/catalogus/beperking/
    """

    id = models.IntegerField(null=False, primary_key=True)

    date_modified = models.DateTimeField(auto_now=True)

    inschrijfnummer = models.IntegerField(null=False)
    beperkingtype = models.ForeignKey(
        Beperkingcode, null=False, on_delete=models.CASCADE)
    datum_in_werking = models.DateField(null=False)
    datum_einde = models.DateField(null=True)

    kadastrale_objecten = models.ManyToManyField(
        brk.KadastraalObject, through='BeperkingKadastraalObject',
        related_name="beperkingen")

    verblijfsobjecten = models.ManyToManyField(
        bag.Verblijfsobject,
        through='BeperkingVerblijfsobject',
        related_name='beperkingen')

    class Meta(object):
        verbose_name = "Beperking"
        verbose_name_plural = "Beperkingen"

    def __str__(self):
        return f"{self.inschrijfnummer} ({self.beperkingtype.omschrijving})"


class Brondocument(models.Model):
    """
    Het document dat aan de beperking ten grondslag ligt.
    """

    id = models.IntegerField(null=False, primary_key=True)  # beperking id

    date_modified = models.DateTimeField(auto_now=True)
    inschrijfnummer = models.IntegerField(null=False)
    bron = models.ForeignKey(
        Broncode, null=True, related_name="documenten",
        on_delete=models.CASCADE)
    documentnaam = models.CharField(max_length=21, null=False)
    persoonsgegevens_afschermen = models.NullBooleanField(null=None)
    soort_besluit = models.CharField(max_length=60, null=True)
    # Seems to be only 1 document for each Beperking.
    beperking = models.ForeignKey(
        Beperking, related_name='documenten', null=True,
        on_delete=models.CASCADE
    )

    @property
    def url(self):
        base_url = 'http://diva.intranet.amsterdam.nl/Brondocumenten/Wkpb'
        return '%s/%s' % (base_url, self.documentnaam)

    @property
    def extern_url(self):
        return f'{settings.DATAPUNT_API_URL}wkpb/brondocument/{self.id}/?as_pdf'

    class Meta:
        verbose_name = "Brondocument"
        verbose_name_plural = "Brondocumenten"

    def __str__(self):
        return self.documentnaam


class BeperkingKadastraalObject(models.Model):
    """
    n:n-relaties: Beperking <> KadastraalObject
    """

    id = models.CharField(max_length=33, null=False, primary_key=True)

    date_modified = models.DateTimeField(auto_now=True)

    beperking = models.ForeignKey(
        Beperking, null=False,
        on_delete=models.CASCADE
    )
    kadastraal_object = models.ForeignKey(
        brk.KadastraalObject, on_delete=models.CASCADE)

    def __str__(self):
        return "{}-{}".format(
            self.beperking_id,
            self.kadastraal_object_id)


class BeperkingVerblijfsobject(models.Model):
    beperking = models.ForeignKey(Beperking, on_delete=models.CASCADE)
    verblijfsobject = models.ForeignKey(
        bag.Verblijfsobject, on_delete=models.CASCADE)
