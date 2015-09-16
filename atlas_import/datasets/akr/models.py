from django.db import models

from datasets.generic import mixins


class SoortCultuurOnbebouwd(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = "Soort cultuur onbebouwd"
        verbose_name_plural = "Soorten cultuur onbebouwd"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class Bebouwingscode(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = "Bebouwingscode"
        verbose_name_plural = "Bebouwingscodes"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class KadastraalObject(mixins.ImportStatusMixin):
    id = models.CharField(max_length=14, primary_key=True)
    gemeentecode = models.CharField(max_length=5)
    sectie = models.CharField(max_length=2)
    perceelnummer = models.IntegerField()
    objectindex_letter = models.CharField(max_length=1)
    objectindex_nummer = models.IntegerField()
    grootte = models.IntegerField(null=True)
    grootte_geschat = models.BooleanField(default=False)
    cultuur_tekst = models.CharField(max_length=65, null=True)
    soort_cultuur_onbebouwd = models.ForeignKey(SoortCultuurOnbebouwd, null=True)
    meer_culturen_onbebouwd = models.BooleanField(default=False)
    bebouwingscode = models.ForeignKey(Bebouwingscode, null=True)
    kaartblad = models.IntegerField(null=True)
    ruitletter = models.CharField(max_length=1, null=True)
    ruitnummer = models.IntegerField(null=True)
    omschrijving_deelperceel = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name = "Kadastraal object"
        verbose_name_plural = "Kadastrale objecten"


class Titel(models.Model):
    code = models.CharField(max_length=11, primary_key=True)
    omschrijving = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Adelijke titel of predikaat"
        verbose_name_plural = "Adelijke titels en predikaten"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class NietNatuurlijkePersoon(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    omschrijving = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Soort niet-natuurlijke persoon"
        verbose_name_plural = "Soorten niet-natuurlijke persoon"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class Land(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    omschrijving = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = "Land"
        verbose_name_plural = "Landen"

    def __str__(self):
        return "{}: {}".format(self.code, self.omschrijving)


class Adres(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    straatnaam = models.CharField(max_length=24, null=True)
    huisnummer = models.IntegerField(null=True)
    huisletter = models.CharField(max_length=1, null=True)
    toevoeging = models.CharField(max_length=4, null=True)
    aanduiding = models.CharField(max_length=2, null=True)
    postcode = models.CharField(max_length=6, null=True)
    woonplaats = models.CharField(max_length=24, null=True)
    adresregel_1 = models.CharField(max_length=39, null=True)
    adresregel_2 = models.CharField(max_length=39, null=True)
    adresregel_3 = models.CharField(max_length=39, null=True)
    land = models.ForeignKey(Land, null=True)
    beschrijving = models.CharField(max_length=40, null=True)


class KadastraalSubject(mixins.ImportStatusMixin):
    SUBJECT_MAN = 'm'
    SUBJECT_VROUW = 'v'
    SUBJECT_ONBEKEND = 'o'
    SUBJECT_AANBIEDER = 'a'

    SUBJECT_CHOICES = (
        (SUBJECT_MAN, 'Man'),
        (SUBJECT_VROUW, 'Vrouw'),
        (SUBJECT_AANBIEDER, 'Aanbieder'),
        (SUBJECT_ONBEKEND, 'Onbekend'),
    )

    id = models.CharField(max_length=14, primary_key=True)
    subjectnummer = models.BigIntegerField(null=False)
    titel_of_predikaat = models.ForeignKey(Titel, null=True)
    geslachtsaanduiding = models.CharField(max_length=1, choices=SUBJECT_CHOICES, null=True, blank=True)
    geslachtsnaam = models.CharField(max_length=128, null=True)
    diacritisch = models.BooleanField(default=False)
    naam_niet_natuurlijke_persoon = models.CharField(max_length=512, null=True)
    soort_subject = models.CharField(max_length=1, choices=SUBJECT_CHOICES, null=True)
    soort_niet_natuurlijke_persoon = models.ForeignKey(NietNatuurlijkePersoon, null=True)
    voorletters = models.CharField(max_length=5, null=True)
    voornamen = models.CharField(max_length=128, null=True)
    voorvoegsel = models.CharField(max_length=10, null=True)
    geboortedatum = models.DateField(null=True)
    geboorteplaats = models.CharField(max_length=24, null=True)
    overleden = models.BooleanField(default=False)
    overlijdensdatum = models.DateField(null=True)
    zetel = models.CharField(max_length=24, null=True)
    woonadres = models.ForeignKey(Adres, null=True, related_name="woonadres")
    postadres = models.ForeignKey(Adres, null=True, related_name="postadres")
    a_nummer = models.BigIntegerField(null=True)

    class Meta:
        verbose_name = "Kadastraal subject"
        verbose_name_plural = "Kadastrale subjecten"
