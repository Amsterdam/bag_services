from django.contrib.gis.db import models as geo
from django.db import models

from datasets.generic import mixins


class Bron(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronnen"


class IndicatieAdresseerbaarObject(models.Model):
    """
    Verblijfsobjecten, Standplaatsen, Ligplaatsen
    kunnen in onderzoek zijn.

    Source table for indicaties

    AOT. Adresseerbaar object
    """
    landelijk_id = models.CharField(max_length=16, primary_key=True, null=False)
    indicatie_geconstateerd = models.BooleanField(null=False)
    indicatie_in_onderzoek = models.BooleanField(null=False)


class Status(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


class RedenAfvoer(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reden Afvoer"
        verbose_name_plural = "Reden Afvoer"


class RedenOpvoer(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reden Opvoer"
        verbose_name_plural = "Reden Opvoer"


class Eigendomsverhouding(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Eigendomsverhouding"
        verbose_name_plural = "Eigendomsverhoudingen"


class Financieringswijze(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Financieringswijze"
        verbose_name_plural = "Financieringswijzes"


class Ligging(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ligging"
        verbose_name_plural = "Ligging"


class Gebruik(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gebruik"
        verbose_name_plural = "Gebruik"


class LocatieIngang(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Locatie Ingang"
        verbose_name_plural = "Locaties Ingang"


class Toegang(mixins.CodeOmschrijvingMixin, models.Model):

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Toegang"
        verbose_name_plural = "Toegang"


class Gemeente(mixins.GeldigheidMixin, models.Model):
    """
    Burgelijke gemeenten
    """

    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)

    date_modified = models.DateTimeField(auto_now=True)
    naam = models.CharField(max_length=40)
    verzorgingsgebied = models.NullBooleanField(default=None)
    vervallen = models.NullBooleanField(default=None)

    class Meta:
        verbose_name = "Gemeente"
        verbose_name_plural = "Gemeentes"

    def __str__(self):
        return self.naam


class Woonplaats(
        mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
        mixins.DocumentStatusMixin, models.Model):

    id = models.CharField(max_length=14, primary_key=True)

    date_modified = models.DateTimeField(auto_now=True)
    landelijk_id = models.CharField(max_length=4, unique=True)
    naam = models.CharField(max_length=80)
    naam_ptt = models.CharField(max_length=18, null=True)
    vervallen = models.NullBooleanField(default=None)
    gemeente = models.ForeignKey(
        Gemeente, related_name='woonplaatsen', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Woonplaats"
        verbose_name_plural = "Woonplaatsen"

    def __str__(self):
        return self.naam


class Hoofdklasse(models.Model):
    """
    De hoofdklasse is een abstracte klasse waar sommige andere
    gebiedsklassen, zoals stadsdeel en buurt, van afstammen.
    Deze afstammelingen erven alle kenmerken over van deze hoofdklasse.
    Het kenmerk 'diva_id' komt bijvoorbeeld voor
    bij alle gebieden.
    """

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    date_modified = models.DateTimeField(auto_now=True)

    objects = geo.Manager()

    class Meta:
        abstract = True


class Stadsdeel(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Door de Amsterdamse gemeenteraad vastgestelde begrenzing van
    een stadsdeel, ressorterend onder een stadsdeelbestuur.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/stadsdeel/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    naam = models.CharField(max_length=40)
    vervallen = models.NullBooleanField(default=None)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    gemeente = models.ForeignKey(
        Gemeente, related_name='stadsdelen', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Stadsdeel"
        verbose_name_plural = "Stadsdelen"

    def __str__(self):
        return f"{self.naam} ({self.code})"


class Buurt(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Een aaneengesloten gedeelte van een buurt, waarvan de grenzen
    zo veel mogelijk gebaseerd zijn op topografische elementen.

    http://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/buurt/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=3, unique=True)
    vollcode = models.CharField(max_length=4)
    naam = models.CharField(max_length=40)
    vervallen = models.NullBooleanField(default=None)
    ingang_cyclus = models.DateField(null=True)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    stadsdeel = models.ForeignKey(
        Stadsdeel, related_name='buurten', on_delete=models.CASCADE)

    buurtcombinatie = models.ForeignKey(
        'Buurtcombinatie', related_name='buurten',
        null=True, on_delete=models.CASCADE)

    gebiedsgerichtwerken = models.ForeignKey(
        'Gebiedsgerichtwerken', related_name='buurten',
        null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Buurt"
        verbose_name_plural = "Buurten"
        ordering = ('vollcode',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.vollcode)

    @property
    def _gemeente(self):
        return self.stadsdeel.gemeente


class Bouwblok(mixins.GeldigheidMixin, Hoofdklasse):
    """
    Een bouwblok is het kleinst mogelijk afgrensbare gebied, in
    zijn geheel tot een buurt behorend, dat geheel of
    grotendeels door bestaande of aan te leggen wegen en/of
    waterlopen is of zal zijn ingesloten en waarop tenminste
    één gebouw staat.

    https://www.amsterdam.nl/stelselpedia/gebieden-index/catalogus/bouwblok/
    """
    id = models.CharField(max_length=14, primary_key=True)
    code = models.CharField(max_length=4, unique=True)  # Bouwbloknummer
    buurt = models.ForeignKey(
        Buurt, related_name='bouwblokken',
        on_delete=models.CASCADE,
        null=True)
    ingang_cyclus = models.DateField(null=True)

    class Meta:
        verbose_name = "Bouwblok"
        verbose_name_plural = "Bouwblokken"
        ordering = ('code',)

    def __str__(self):
        return "{}".format(self.code)

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None


class OpenbareRuimte(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
                     mixins.DocumentStatusMixin, models.Model):
    """
    Een OPENBARE RUIMTE is een door het bevoegde gemeentelijke orgaan als
    zodanig aangewezen en van een naam voorziene
    buitenruimte die binnen één woonplaats is gelegen.

    Als openbare ruimte worden onder meer aangemerkt weg, water,
    terrein, spoorbaan en landschappelijk gebied.

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

    date_modified = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=2, null=True, choices=TYPE_CHOICES)
    naam = models.CharField(max_length=150)
    code = models.CharField(max_length=5, unique=True)
    straat_nummer = models.CharField(max_length=10, null=True)
    naam_nen = models.CharField(max_length=24)
    naam_ptt = models.CharField(max_length=17)
    vervallen = models.NullBooleanField(default=None)
    bron = models.ForeignKey(Bron, null=True, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)
    woonplaats = models.ForeignKey(
        Woonplaats, related_name="openbare_ruimtes",
        on_delete=models.CASCADE
    )
    geometrie = geo.MultiPolygonField(null=True, srid=28992)
    omschrijving = models.TextField(null=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Openbare Ruimte"
        verbose_name_plural = "Openbare Ruimtes"
        ordering = ('naam', 'id')

    def __str__(self):
        return self.naam

    def dict_for_index(self, deep=True):
        """
        Converts the object into a dict to be indexed
        default is to also convert foreign key objects

        If deep is set to false, it will not add foreign key objects
        but instead add their ids
        """
        dct = {}
        for field in self._meta.fields:
            if field.get_internal_type() == 'ForeignKey':
                if deep:
                    pass
                else:
                    dct[field.name] = getattr(
                        self, '{}_id'.format(field.name), None)
            else:
                dct[field.name] = getattr(self, field.name, '')
        return dct


class Gebiedsgerichtwerken(models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM', 'CODE', 'STADSDEEL',
     'INGSDATUM', 'EINDDATUM', 'DOCNR', 'DOCDATUM']
    """

    id = models.CharField(max_length=4, primary_key=True)
    code = models.CharField(max_length=4)
    naam = models.CharField(max_length=100)

    date_modified = models.DateTimeField(auto_now=True)

    stadsdeel = models.ForeignKey(
        Stadsdeel, related_name='gebiedsgerichtwerken',
        on_delete=models.CASCADE,
    )

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Gebiedsgerichtwerken"
        verbose_name_plural = "Gebiedsgerichtwerken"
        ordering = ('code',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.code)


class Grootstedelijkgebied(models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    id = models.SlugField(max_length=100, primary_key=True)
    naam = models.CharField(max_length=100)
    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    date_modified = models.DateTimeField(auto_now=True)
    objects = geo.Manager()

    class Meta:
        verbose_name = "Grootstedelijkgebied"
        verbose_name_plural = "Grootstedelijke gebieden"

    def __str__(self):
        return "{}".format(self.naam)


class Nummeraanduiding(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
                       mixins.DocumentStatusMixin, models.Model):
    """
    Een nummeraanduiding, in de volksmond ook wel adres genoemd, is een door
    het bevoegde gemeentelijke orgaan als
    zodanig toegekende aanduiding van een verblijfsobject,
    standplaats of ligplaats.

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
    huisnummer = models.IntegerField(db_index=True)
    huisletter = models.CharField(max_length=1, null=True)
    huisnummer_toevoeging = models.CharField(max_length=4, null=True, db_index=True)
    postcode = models.CharField(max_length=6, null=True, db_index=True)
    type = models.CharField(
        max_length=2, null=True, choices=OBJECT_TYPE_CHOICES)
    adres_nummer = models.CharField(max_length=10, null=True)
    vervallen = models.NullBooleanField(default=None)
    bron = models.ForeignKey(Bron, null=True, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)
    openbare_ruimte = models.ForeignKey(
        OpenbareRuimte, related_name='adressen',
        on_delete=models.CASCADE
    )

    date_modified = models.DateTimeField(auto_now=True)

    ligplaats = models.ForeignKey(
        'Ligplaats', null=True, related_name='adressen',
        on_delete=models.CASCADE
    )

    standplaats = models.ForeignKey(
        'Standplaats', null=True, related_name='adressen',
        on_delete=models.CASCADE
    )

    verblijfsobject = models.ForeignKey(
        'Verblijfsobject', null=True, related_name='adressen',
        on_delete=models.CASCADE
    )

    hoofdadres = models.NullBooleanField(default=None)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)

    _geom = geo.GeometryField(null=True, srid=28992)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Nummeraanduiding"
        verbose_name_plural = "Nummeraanduidingen"
        ordering = (
            '_openbare_ruimte_naam', 'huisnummer',
            'huisletter', 'huisnummer_toevoeging')
        index_together = (
            ('_openbare_ruimte_naam', 'huisnummer',
             'huisletter', 'huisnummer_toevoeging')
        )

    def __str__(self):
        return self.adres()

    def adres(self):
        return '%s %s' % (
            self._openbare_ruimte_naam, self._display_toevoeging())

    def dict_for_index(self, deep=True):
        """
        Converts the object into a dict to be indexed
        default is to also convert foreign key objects

        If deep is set to false, it will not add foreign key objects
        but instead add their ids
        """
        dct = {
            'postcode': "{} {}".format(
                self.postcode, self.toevoeging),
            'huisnummer': self.huisnummer,
        }
        if deep:
            # Creating a deep copy
            dct.update({
                'straatnaam': self.openbare_ruimte.naam,
                'straatnaam_nen': self.openbare_ruimte.naam_nen,
                'straatnaam_ptt': self.openbare_ruimte.naam_ptt
            })
        else:
            dct.update({
                'openbaar_ruimte': self.openbaar_ruimte_id
            })
        return dct

    def _display_toevoeging(self):

        toevoegingen = []

        toevoeging = self.huisnummer_toevoeging

        if self.huisnummer:
            toevoegingen.append(str(self.huisnummer))

        if self.huisletter:
            toevoegingen.append(str(self.huisletter))

        if toevoeging:
            toevoegingen.append('-%s' % toevoeging)
        return "".join(toevoegingen)

    @property
    def toevoeging(self):
        """Toevoeging samen voeging.

        Toevoeing represents the total added string to
        a street/openbareruimte name.
        """

        toevoegingen = []

        toevoeging = self.huisnummer_toevoeging

        if self.huisnummer:
            toevoegingen.append(str(self.huisnummer))

        if self.huisletter:
            toevoegingen.append(str(self.huisletter))

        def addnumber(lastdigits, split_tv):
            digits = "".join(lastdigits)
            if digits:
                split_tv.append(digits)

        if toevoeging:
            tv = str(toevoeging)
            split_tv = []
            lastdigits = []
            prev = ""

            for c in tv:
                if c.isdigit():
                    lastdigits.append(c)
                    continue
                else:
                    addnumber(lastdigits, split_tv)
                    lastdigits = []
                    split_tv.append(c)

            # add left-over digits if any.
            addnumber(lastdigits, split_tv)

            # create the toevoeging
            toevoegingen.extend(split_tv)

        return ' '.join(toevoegingen)

    @property
    def adresseerbaar_object(self):
        return self.ligplaats or self.standplaats or self.verblijfsobject

    @property
    def vbo_status(self):
        a = self.adresseerbaar_object
        return a.status

    @property
    def buurt(self):
        a = self.adresseerbaar_object
        return a.buurt if a else None

    @property
    def _geometrie(self):
        a = self.adresseerbaar_object
        return a.geometrie if a else None

    @property
    def stadsdeel(self):
        b = self.buurt
        return b.stadsdeel if b else None

    @property
    def woonplaats(self):
        o = self.openbare_ruimte
        return o.woonplaats if o else None

    @property
    def buurtcombinatie(self):
        b = self.buurt
        return b.buurtcombinatie if b else None

    @property
    def bouwblok(self):
        return self.verblijfsobject.bouwblok if self.verblijfsobject else None

    @property
    def gemeente(self):
        s = self.stadsdeel
        return s.gemeente if s else None

    @property
    def gebiedsgerichtwerken(self):
        a = self.adresseerbaar_object
        return a._gebiedsgerichtwerken if a else None

    @property
    def grootstedelijkgebied(self):
        a = self.adresseerbaar_object
        return a._grootstedelijkgebied if a else None


class AdresseerbaarObjectMixin(object):
    @property
    def hoofdadres(self):
        # noinspection PyUnresolvedReferences
        candidates = [a for a in self.adressen.all() if a.hoofdadres]
        return candidates[0] if candidates else None

    @property
    def nevenadressen(self):
        # noinspection PyUnresolvedReferences
        return [a for a in self.adressen.all() if not a.hoofdadres]

    def __str__(self):
        if self.hoofdadres:
            return self.hoofdadres.adres()
        return "adres onbekend"


class Ligplaats(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
                mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een LIGPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig
    aangewezen plaats in het water al dan niet aangevuld met een op de
    oever aanwezig terrein of een gedeelte daarvan, die bestemd is voor
    het permanent afmeren van een voor woon-, bedrijfsmatige of
    recreatieve doeleinden geschikt vaartuig.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-1/
    """

    id = models.CharField(max_length=14, primary_key=True)

    date_modified = models.DateTimeField(auto_now=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.NullBooleanField(default=None)
    bron = models.ForeignKey(Bron, null=True, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)

    indicatie_geconstateerd = models.NullBooleanField(default=None)
    indicatie_in_onderzoek = models.NullBooleanField(default=None)

    buurt = models.ForeignKey(
        Buurt, null=True, related_name='ligplaatsen',
        on_delete=models.CASCADE
    )

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='ligplaatsen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='ligplaatsen', null=True,
        on_delete=models.CASCADE
    )

    geometrie = geo.PolygonField(null=True, srid=28992)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)
    _huisnummer = models.IntegerField(null=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Ligplaats"
        verbose_name_plural = "Ligplaatsen"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')

        index_together = [
            ('_openbare_ruimte_naam', '_huisnummer',
             '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):

        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += ' ' + self._huisnummer_toevoeging
        return result

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Standplaats(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
                  mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een STANDPLAATS is een door het bevoegde gemeentelijke orgaan als zodanig
    aangewezen terrein of gedeelte daarvan dat bestemd is voor het permanent
    plaatsen van een niet direct en niet duurzaam met de aarde verbonden en
    voor woon-, bedrijfsmatige, of recreatieve doeleinden geschikte ruimte.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-4/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True, null=True)
    vervallen = models.NullBooleanField(default=None)
    bron = models.ForeignKey(Bron, null=True, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)
    buurt = models.ForeignKey(
        Buurt, null=True, related_name='standplaatsen',
        on_delete=models.CASCADE
    )

    date_modified = models.DateTimeField(auto_now=True)

    indicatie_geconstateerd = models.NullBooleanField(default=None)
    indicatie_in_onderzoek = models.NullBooleanField(default=None)

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='standplaatsen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='standplaatsen', null=True,
        on_delete=models.CASCADE
    )

    geometrie = geo.PolygonField(null=True, srid=28992)

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, null=True)
    _huisnummer = models.IntegerField(null=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Standplaats"
        verbose_name_plural = "Standplaatsen"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')
        index_together = [
            ('_openbare_ruimte_naam', '_huisnummer',
             '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):
        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += ' ' + self._huisnummer_toevoeging
        return result

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Verblijfsobject(mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
                      mixins.DocumentStatusMixin, AdresseerbaarObjectMixin, models.Model):
    """
    Een VERBLIJFSOBJECT is de kleinste binnen één of meer panden gelegen en
    voor woon-, bedrijfsmatige, of recreatieve
    doeleinden geschikte eenheid van gebruik die ontsloten wordt via een eigen
    afsluitbare toegang vanaf de openbare weg, een erf of een gedeelde
    verkeersruimte, onderwerp kan zijn van goederenrechtelijke
    rechtshandelingen en in functioneel opzicht zelfstandig is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-0/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    oppervlakte = models.PositiveIntegerField(null=True)
    bouwlaag_toegang = models.IntegerField(null=True)
    status_coordinaat_code = models.CharField(max_length=3, null=True)
    status_coordinaat_omschrijving = models.CharField(
        max_length=150, null=True)
    verhuurbare_eenheden = models.PositiveIntegerField(null=True)
    bouwlagen = models.PositiveIntegerField(null=True)
    type_woonobject_code = models.CharField(max_length=2, null=True)
    type_woonobject_omschrijving = models.CharField(max_length=150, null=True)
    woningvoorraad = models.NullBooleanField(default=None)
    aantal_kamers = models.PositiveIntegerField(null=True)
    vervallen = models.PositiveIntegerField(default=False)
    reden_afvoer = models.ForeignKey(
        RedenAfvoer, null=True, on_delete=models.CASCADE)

    date_modified = models.DateTimeField(auto_now=True)

    reden_opvoer = models.ForeignKey(
        RedenOpvoer, null=True, on_delete=models.CASCADE)
    bron = models.ForeignKey(Bron, null=True, on_delete=models.CASCADE)
    eigendomsverhouding = models.ForeignKey(
        Eigendomsverhouding, null=True, on_delete=models.CASCADE)
    financieringswijze = models.ForeignKey(
        Financieringswijze, null=True, on_delete=models.CASCADE)

    gebruik = models.ForeignKey(Gebruik, null=True, on_delete=models.CASCADE)
    locatie_ingang = models.ForeignKey(
        LocatieIngang, null=True, on_delete=models.CASCADE)
    ligging = models.ForeignKey(
        Ligging, null=True, on_delete=models.CASCADE)
    toegang = models.ForeignKey(
        Toegang, null=True, on_delete=models.CASCADE)

    status = models.ForeignKey(
        Status, null=True, on_delete=models.CASCADE)

    buurt = models.ForeignKey(
        Buurt, null=True, related_name='verblijfsobjecten',
        on_delete=models.CASCADE
    )

    indicatie_geconstateerd = models.NullBooleanField(default=None)
    indicatie_in_onderzoek = models.NullBooleanField(default=None)

    panden = models.ManyToManyField(
        'Pand', related_name='verblijfsobjecten',
        through='VerblijfsobjectPandRelatie')

    geometrie = geo.PointField(null=True, srid=28992)

    _gebiedsgerichtwerken = models.ForeignKey(
        Gebiedsgerichtwerken, related_name='adressen', null=True,
        on_delete=models.CASCADE
    )

    _grootstedelijkgebied = models.ForeignKey(
        Grootstedelijkgebied, related_name='adressen', null=True,
        on_delete=models.CASCADE
    )

    # gedenormaliseerde velden
    _openbare_ruimte_naam = models.CharField(max_length=150, db_index=True, null=True)
    _huisnummer = models.IntegerField(null=True, db_index=True)
    _huisletter = models.CharField(max_length=1, null=True)
    _huisnummer_toevoeging = models.CharField(max_length=4, null=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Verblijfsobject"
        verbose_name_plural = "Verblijfsobjecten"
        ordering = (
            '_openbare_ruimte_naam', '_huisnummer',
            '_huisletter', '_huisnummer_toevoeging')
        index_together = [
            (
                '_openbare_ruimte_naam', '_huisnummer',
                '_huisletter', '_huisnummer_toevoeging')
        ]

    def __str__(self):
        result = '{} {}'.format(self._openbare_ruimte_naam, self._huisnummer)
        if self._huisletter:
            result += self._huisletter
        if self._huisnummer_toevoeging:
            result += '-' + self._huisnummer_toevoeging
        return result

    # store pand for bouwblok reference
    _pand = None

    @property
    def willekeurig_pand(self):
        """
        Geeft het pand van dit verblijfsobject. Indien er meerdere
        panden zijn, wordt een willekeurig pand gekozen.
        """
        if not self.panden.count():
            return None

        if not self._pand:
            self._pand = self.panden.select_related(
                'bouwblok',
            )[0]

        return self._pand

    @property
    def bouwblok(self):
        if not self.willekeurig_pand:
            return None

        return self.willekeurig_pand.bouwblok

    @property
    def _buurtcombinatie(self):
        return self.buurt.buurtcombinatie if self.buurt else None

    @property
    def _stadsdeel(self):
        return self.buurt.stadsdeel if self.buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _woonplaats(self):
        return self.hoofdadres.woonplaats if self.hoofdadres else None


class Pand(
        mixins.GeldigheidMixin, mixins.MutatieGebruikerMixin,
        mixins.DocumentStatusMixin, models.Model):
    """
    Een PAND is de kleinste bij de totstandkoming functioneel en
    bouwkundig-constructief zelfstandige eenheid die direct
    en duurzaam met de aarde is verbonden en betreedbaar en
    afsluitbaar is.

    http://www.amsterdam.nl/stelselpedia/bag-index/catalogus-bag/objectklasse-pand/
    """

    id = models.CharField(max_length=14, primary_key=True)
    landelijk_id = models.CharField(max_length=16, unique=True)
    bouwjaar = models.PositiveIntegerField(null=True)
    laagste_bouwlaag = models.IntegerField(null=True)
    hoogste_bouwlaag = models.IntegerField(null=True)
    pandnummer = models.CharField(max_length=10, null=True)
    vervallen = models.NullBooleanField(default=None)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)

    bouwblok = models.ForeignKey(
        Bouwblok, null=True, related_name="panden", on_delete=models.CASCADE)

    geometrie = geo.PolygonField(null=True, srid=28992)

    date_modified = models.DateTimeField(auto_now=True)

    pandnaam = models.CharField(max_length=250, null=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Pand"
        verbose_name_plural = "Panden"

    def __str__(self):
        return "{}".format(self.landelijk_id)

    @property
    def _buurt(self):
        return self.bouwblok.buurt if self.bouwblok else None

    @property
    def _buurtcombinatie(self):
        return self._buurt.buurtcombinatie if self._buurt else None

    @property
    def _stadsdeel(self):
        return self._buurt.stadsdeel if self._buurt else None

    @property
    def _gemeente(self):
        return self._stadsdeel.gemeente if self._stadsdeel else None

    @property
    def _monumenten(self):
        return self


class VerblijfsobjectPandRelatie(models.Model):
    id = models.CharField(max_length=29, primary_key=True)
    pand = models.ForeignKey(Pand, on_delete=models.CASCADE)
    verblijfsobject = models.ForeignKey(
        Verblijfsobject, on_delete=models.CASCADE)

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Verblijfsobject-Pand relatie"
        verbose_name_plural = "Verblijfsobject-Pand relaties"

    def __init__(self, *args, **kwargs):
        super(VerblijfsobjectPandRelatie, self).__init__(*args, **kwargs)

        if self.pand_id and self.verblijfsobject_id:
            self.id = '{pid}_{vid}'.format(pid=self.pand_id,
                                           vid=self.verblijfsobject_id)

    def __str__(self):
        return "Pand-Verblijfsobject({}-{})".format(
            self.pand_id, self.verblijfsobject_id)


class Buurtcombinatie(mixins.GeldigheidMixin, models.Model):
    """
    model for data from shp files

    layer.fields:

    ['ID', 'NAAM', 'CODE', 'VOLLCODE', 'DOCNR', 'DOCDATUM',
     'INGSDATUM', 'EINDDATUM']
    """

    id = models.CharField(max_length=14, primary_key=True)
    naam = models.CharField(max_length=100)
    code = models.CharField(max_length=2)
    vollcode = models.CharField(max_length=3)
    brondocument_naam = models.CharField(max_length=100, null=True)
    brondocument_datum = models.DateField(null=True)
    ingang_cyclus = models.DateField(null=True)

    stadsdeel = models.ForeignKey(
        Stadsdeel, null=True, related_name="buurtcombinaties",
        on_delete=models.CASCADE
    )

    date_modified = models.DateTimeField(auto_now=True)

    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Buurtcombinatie"
        verbose_name_plural = "Buurtcombinaties"
        ordering = ('code',)

    def __str__(self):
        return "{} ({})".format(self.naam, self.code)

    def _gemeente(self):
        if self.stadsdeel:
            return self.stadsdeel.gemeente


class Unesco(models.Model):
    """
    model for data from shp files

    layer.fields:

    ['NAAM']
    """

    id = models.SlugField(max_length=100, primary_key=True)
    naam = models.CharField(max_length=100)
    geometrie = geo.MultiPolygonField(null=True, srid=28992)

    date_modified = models.DateTimeField(auto_now=True)

    objects = geo.Manager()

    class Meta:
        verbose_name = "Unesco"
        verbose_name_plural = "Unesco"

    def __str__(self):
        return "{}".format(self.naam)


class Gebruiksdoel(models.Model):
    verblijfsobject = models.ForeignKey(
        Verblijfsobject, max_length=16, related_name='gebruiksdoelen',
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=4)
    omschrijving = models.CharField(max_length=150)
    code_plus = models.CharField(max_length=4, null=True)
    omschrijving_plus = models.CharField(max_length=150, null=True)
