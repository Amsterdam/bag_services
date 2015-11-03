from django.db import models
from django.contrib.gis.db import models as geo

from datasets.generic import mixins
from datasets.bag import models as bag


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
    id = models.CharField(max_length=17, primary_key=True)
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
    geometrie = geo.PointField(null=True, srid=28992)
    verblijfsobjecten = models.ManyToManyField('bag.Verblijfsobject', through="KadastraalObjectVerblijfsobject",
                                               related_name="kadastrale_objecten")

    class Meta:
        verbose_name = "Kadastraal object"
        verbose_name_plural = "Kadastrale objecten"
        ordering = ('id',)


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
    voorletters = models.CharField(max_length=15, null=True)
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

        permissions = (
            ('view_sensitive_details', 'Kan privacy-gevoelige data inzien'),
        )

    def natuurlijk_persoon(self):
        return not self.naam_niet_natuurlijke_persoon

    def volledige_naam(self):
        if not self.natuurlijk_persoon():
            return self.naam_niet_natuurlijke_persoon

        titel = self.titel_of_predikaat.omschrijving if self.titel_of_predikaat else None

        return " ".join([part for part in (titel,
                                           self.voorletters or self.voornamen,
                                           self.voorvoegsel,
                                           self.geslachtsnaam) if part])

    def rechten_lazy(self):
        return self.rechten.select_related('kadastraal_object',
                                           'kadastraal_subject',
                                           'transactie',
                                           'soort_recht')

    def num_rechten(self):
        return len(self.rechten.all())


class SoortStuk(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    omschrijving = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Soort stuk'
        verbose_name_plural = 'Soorten stukken'

    def __str__(self):
        return '{}: {}'.format(self.code, self.omschrijving)


class Transactie(mixins.ImportStatusMixin):
    id = models.CharField(max_length=14, primary_key=True)
    registercode = models.CharField(max_length=14, null=False)
    stukdeel_1 = models.CharField(max_length=5, null=True)
    stukdeel_2 = models.CharField(max_length=5, null=True)
    stukdeel_3 = models.CharField(max_length=5, null=True)
    soort_stuk = models.ForeignKey(SoortStuk, null=True)
    ontvangstdatum = models.DateField(null=True)
    verlijdensdatum = models.DateField(null=True)
    meer_kadastrale_objecten = models.BooleanField(default=False)
    koopjaar = models.SmallIntegerField(null=True)
    koopsom = models.IntegerField(null=True)
    belastingplichtige = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Transactie"
        verbose_name_plural = "Transacties"


class SoortRecht(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    omschrijving = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Soort recht'
        verbose_name_plural = 'Soorten recht'

    def __str__(self):
        return '{}: {}'.format(self.code, self.omschrijving)


class ZakelijkRecht(mixins.ImportStatusMixin):
    id = models.CharField(max_length=14, primary_key=True)
    identificatie = models.CharField(max_length=14)
    soort_recht = models.ForeignKey(SoortRecht, null=True)
    volgnummer = models.IntegerField(null=True)
    aandeel_medegerechtigden = models.CharField(max_length=16, null=True)
    aandeel_subject = models.CharField(max_length=16, null=True)
    einde_filiatie = models.BooleanField(default=False)
    sluimerend = models.BooleanField(default=False)
    kadastraal_object = models.ForeignKey(KadastraalObject, related_name="rechten")
    kadastraal_subject = models.ForeignKey(KadastraalSubject, related_name="rechten")
    transactie = models.ForeignKey(Transactie, related_name="rechten")

    class Meta:
        verbose_name = "Zakelijke recht"
        verbose_name_plural = "Zakelijke rechten"


class KadastraalObjectVerblijfsobject(mixins.ImportStatusMixin):
    id = models.UUIDField(primary_key=True)
    kadastraal_object = models.ForeignKey(KadastraalObject)
    verblijfsobject = models.ForeignKey(bag.Verblijfsobject, null=True)
