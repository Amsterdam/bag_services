from django.db import models

from datasets.generic import mixins


class SoortCultuurOnbebouwdDomein(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = "Soort cultuur onbebouwd domein"
        verbose_name_plural = "Soorten cultuur onbebouwd domein"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class BebouwingscodeDomein(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = "Bebouwingscode domein"
        verbose_name_plural = "Bebouwingscodes domein"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class KadastraalObject(mixins.ImportStatusMixin):
    id = models.CharField(max_length=14, primary_key=True)
    gemeentecode_domein = models.CharField(max_length=5)
    sectie = models.CharField(max_length=2)
    perceelnummer = models.IntegerField()
    objectindex_letter = models.CharField(max_length=1)
    objectindex_nummer = models.IntegerField()
    grootte = models.IntegerField(null=True)
    grootte_geschat = models.BooleanField(default=False)
    cultuur_tekst = models.CharField(max_length=65, null=True)
    soort_cultuur_onbebouwd_domein = models.ForeignKey(SoortCultuurOnbebouwdDomein, null=True)
    meer_culturen_onbebouwd = models.BooleanField(default=False)
    bebouwingscode_domein = models.ForeignKey(BebouwingscodeDomein, null=True)
    kaartblad = models.IntegerField(null=True)
    ruitletter = models.CharField(max_length=1, null=True)
    ruitnummer = models.IntegerField(null=True)
    omschrijving_deelperceel = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name = "Kadastraal object"
        verbose_name_plural = "Kadastrale objecten"
